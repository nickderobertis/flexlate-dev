import threading
import time
from pathlib import Path
from typing import Optional, Union, cast

import patch
from git import Repo
from unidiff import PatchedFile, PatchSet

from flexlate_dev.dirutils import change_directory_to
from flexlate_dev.ext_flexlate import (
    get_flexlate_branch_names_from_project_path,
    get_non_flexlate_commits_between_commits,
    get_render_relative_root_in_template_from_project_path,
)
from flexlate_dev.ext_threading import PropagatingThread
from flexlate_dev.gitutils import stage_and_commit_all, temporary_branch_from_commits
from flexlate_dev.logger import log
from flexlate_dev.server.sync import SyncServerManager, pause_sync
from flexlate_dev.styles import INFO_STYLE, print_styled


def get_last_commit_sha(repo: Repo) -> str:
    return repo.head.commit.hexsha


def get_diff_between_commits(repo: Repo, sha1: str, sha2: str) -> PatchSet:
    diff_str = repo.git.diff(sha1, sha2)
    return PatchSet(diff_str)


def commit_in_one_repo_with_another_repo_commit_message(
    repo: Repo,
    other_repo: Repo,
    commit_sha: str,
) -> None:
    commit_message = repo.commit(commit_sha).message
    # Convert commit message to str if it is a bytes object
    if isinstance(commit_message, bytes):
        message_str = commit_message.decode("utf-8")
    else:
        message_str = commit_message
    print_styled(f"Committing change: {message_str}", INFO_STYLE)
    stage_and_commit_all(other_repo, message_str)


def _relative_path_from_diff_path(diff_path: str) -> Optional[Path]:
    """
    Converts a git diff path in the following formats:
    a/path/file.txt
    b/file.txt
    b/path/file.txt

    To the relative paths:
    path/file.txt
    file.txt
    path/file.txt

    :param diff_path: diff path from git diff
    :return: relative with without a/ or b/ prefix
    """
    if diff_path.startswith("a/"):
        return Path(diff_path[2:])
    elif diff_path.startswith("b/"):
        return Path(diff_path[2:])
    elif diff_path == "/dev/null":
        return None
    else:
        raise ValueError(f"Unknown diff path {diff_path}")


def apply_diff_between_commits_to_separate_project(
    repo: Repo, sha1: str, sha2: str, project_path: Path
) -> None:
    diff = get_diff_between_commits(repo, sha1, sha2)
    apply_diff_to_project(project_path, diff)


def apply_diff_to_project(project_path: Path, diff: PatchSet) -> None:
    log.debug(f"Applying to {project_path}:\n{diff}")
    for file_diff in diff:
        apply_file_diff_to_project(project_path, file_diff)


def _get_content_from_file_added_diff(diff: PatchedFile) -> str:
    # Combine lines
    return "\n".join(["".join([line.value for line in hunk]) for hunk in diff])


def _apply_patch(diff: Union[PatchedFile, PatchSet, str], project_path: Path) -> None:
    # TODO: for some reason the patch library will add a new line to the end of the file
    #  even when it is not supposed to have one
    patch_set = patch.fromstring(str(diff).encode("utf-8"))
    with change_directory_to(project_path):
        patch_set.apply()
    return


def is_pure_rename(diff: PatchedFile) -> bool:
    return diff.is_rename and "similarity index 100%" in str(diff.patch_info)


def apply_file_diff_to_project(project_path: Path, diff: PatchedFile) -> None:
    def project_file_path(diff_path: str) -> Optional[Path]:
        file_path = _relative_path_from_diff_path(diff_path)
        if file_path is None:
            return None
        return project_path / file_path

    log.debug(
        f"Applying diff {diff.source_file} to {diff.target_file} in {project_path}"
    )
    target_path = project_file_path(diff.target_file)
    source_path = project_file_path(diff.source_file)

    def rename():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(target_path)

    if diff.is_added_file:
        out_path = cast(Path, target_path)
        content = _get_content_from_file_added_diff(diff)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content)
    elif diff.is_removed_file:
        out_path = cast(Path, source_path)
        out_path.unlink()
    elif is_pure_rename(diff):
        rename()
    elif diff.is_rename:
        # Rename with modifications
        rename()
        _apply_patch(diff, project_path)
    elif diff.is_modified_file:
        # Modifications in place
        _apply_patch(diff, project_path)
    else:
        raise NotImplementedError("Unknown diff type")


class BackSyncServer:
    def __init__(
        self,
        template_path: Path,
        project_folder: Path,
        sync_manager: SyncServerManager,
        auto_commit: bool = True,
        check_interval_seconds: int = 1,
    ):
        super().__init__()
        self.template_path = template_path
        self.project_folder = project_folder
        self.sync_manager = sync_manager
        self.auto_commit = auto_commit
        self.check_interval_seconds = check_interval_seconds

        self.project_repo: Repo = Repo(self.project_folder)
        self.template_repo: Repo = Repo(
            self.template_path, search_parent_directories=True
        )
        self.last_commit = get_last_commit_sha(self.project_repo)
        self.thread: Optional[threading.Thread] = None
        self.is_syncing = False
        self.is_sleeping = False
        self.template_output_path = (
            self.template_path
            / get_render_relative_root_in_template_from_project_path(
                self.project_folder
            )
        )
        self.branch_names = get_flexlate_branch_names_from_project_path(
            self.project_folder
        )

    def start(self):
        if self.thread is not None:
            raise RuntimeError("Already started")
        # Run start_sync on a background thread
        self.thread = PropagatingThread(target=self.start_sync, daemon=True)
        self.thread.start()

    def stop(self):
        if self.thread is not None:
            log.debug("Killing back sync thread")
            self.thread.join(timeout=0.1)
            self.thread = None

    def start_sync(self):
        while True:
            new_commit = get_last_commit_sha(self.project_repo)
            if self.last_commit == new_commit:
                self._sleep()
                continue
            self.sync()
            self.last_commit = new_commit
            self._sleep()

    def sync(self):
        self.is_syncing = True
        try:
            self._sync()
        finally:
            self.is_syncing = False

    def _sleep(self):
        self.is_sleeping = True
        time.sleep(self.check_interval_seconds)
        self.is_sleeping = False

    def _sync(self):
        last_commit = self.project_repo.commit(self.last_commit)
        new_commit = self.project_repo.commit(get_last_commit_sha(self.project_repo))
        new_commits = get_non_flexlate_commits_between_commits(
            self.project_repo,
            last_commit,
            new_commit,
            self.branch_names.merged_branch_name,
            self.branch_names.template_branch_name,
        )
        if not new_commits:
            log.debug("Skipping back-sync as there are no non-flexlate commits")
            return
        print_styled(
            f"Back-syncing commits: {[f'{commit.hexsha}: {commit.message}' for commit in new_commits]}",
            INFO_STYLE,
        )
        with pause_sync(self.sync_manager):
            with temporary_branch_from_commits(
                self.project_repo, last_commit, new_commits
            ) as branch_info:
                last_commit_sha = self.last_commit
                for new_commit_sha in branch_info.commit_shas:
                    apply_diff_between_commits_to_separate_project(
                        self.project_repo,
                        last_commit_sha,
                        new_commit_sha,
                        self.template_output_path,
                    )
                    if self.auto_commit:
                        commit_in_one_repo_with_another_repo_commit_message(
                            self.project_repo, self.template_repo, new_commit_sha
                        )
                    last_commit_sha = new_commit_sha

    def __enter__(self) -> "BackSyncServer":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
