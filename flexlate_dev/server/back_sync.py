import time
from copy import deepcopy
from pathlib import Path
from typing import Optional

import patch
from flexlate import Flexlate
from git import Repo
from unidiff import PatchedFile, PatchSet

from flexlate_dev.config import FlexlateDevConfig
from flexlate_dev.dirutils import change_directory_to
from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.logger import log


def get_last_commit_sha(repo: Repo) -> str:
    return repo.head.commit.hexsha


def get_diff_between_commits(repo: Repo, sha1: str, sha2: str) -> PatchSet:
    diff_str = repo.git.diff(sha1, sha2)
    return PatchSet(diff_str)


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
    for file_diff in diff:
        apply_file_diff_to_project(project_path, file_diff)


def _get_content_from_file_added_diff(diff: PatchedFile) -> str:
    # Combine lines
    return "\n".join(["".join([line.value for line in hunk]) for hunk in diff])


def apply_file_diff_to_project(project_path: Path, diff: PatchedFile) -> None:
    def project_file_path(diff_path: str) -> Optional[Path]:
        file_path = _relative_path_from_diff_path(diff_path)
        if file_path is None:
            return None
        return project_path / file_path

    def apply_patch():
        patch_set = patch.fromstring(str(diff).encode("utf-8"))
        with change_directory_to(project_path):
            patch_set.apply()
        return

    log.debug(
        f"Applying diff {diff.source_file} to {diff.target_file} in {project_path}"
    )
    target_path = project_file_path(diff.target_file)
    source_path = project_file_path(diff.source_file)

    if diff.is_added_file:
        out_path = target_path
        content = _get_content_from_file_added_diff(diff)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content)
    elif diff.is_removed_file:
        out_path = source_path
        out_path.unlink()
    elif diff.is_rename:
        # TODO: rename with modifications?
        target_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(target_path)
    elif diff.is_modified_file:
        out_path = target_path
        apply_patch()
    else:
        raise NotImplementedError("Unknown diff type")


class BackSyncServer:
    def __init__(
        self,
        config: FlexlateDevConfig,
        template_path: Path,
        out_folder: Path,
        run_config_name: Optional[str] = None,
        no_input: bool = False,
        auto_commit: bool = True,
        check_interval_seconds: int = 1,
    ):
        super().__init__()
        self.config = config
        self.run_config_name = run_config_name
        self.run_config = config.get_full_run_config(
            ExternalCLICommandType.SERVE, run_config_name
        )
        self.template_path = template_path
        self.out_folder = out_folder
        self.no_input = no_input
        self.auto_commit = auto_commit
        self.check_interval_seconds = check_interval_seconds

        self.repo: Repo = Repo(self.out_folder)
        self.fxt = Flexlate()
        self.last_commit = get_last_commit_sha(self.repo)

    def start(self):
        while True:
            if self._update_commit_get_changed():
                self.sync()
            time.sleep(self.check_interval_seconds)

    def sync(self):
        pass

    def _update_commit_get_changed(self) -> bool:
        if self.last_commit != get_last_commit_sha(self.repo):
            self.last_commit = get_last_commit_sha(self.repo)
            return True
        return False
