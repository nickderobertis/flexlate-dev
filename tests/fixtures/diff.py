from typing import Final

import pytest
from git import Repo
from unidiff import PatchedFile, PatchSet

from flexlate_dev.server.back_sync import get_diff_between_commits
from tests.fixtures.repo import flexlate_dev_repo


def _get_diff_between_commit_and_parent(repo: Repo, sha: str) -> PatchSet:
    commit = repo.commit(sha)
    parent = commit.parents[0]
    return get_diff_between_commits(repo, parent.hexsha, sha)


ADDED_FILE_SHA: Final[str] = "941efdf4533463986e81cfcc62f129ef899bc92b"
REMOVED_FILE_SHA: Final[str] = "3d3157a424270d295079cd29ce49f6f58b6aa616"
RENAMED_FILE_SHA: Final[str] = "6d0b0b85b6a64ca02ddb8947c3cfddd1f64ea851"
MODIFIED_FILE_SHA: Final[str] = "cdc3b85ff0db4d9a38720d9a70010849193e4fdf"


@pytest.fixture(scope="session")
def file_added_diff(flexlate_dev_repo: Repo) -> PatchedFile:
    patch_set = _get_diff_between_commit_and_parent(flexlate_dev_repo, ADDED_FILE_SHA)
    return patch_set[0]


@pytest.fixture(scope="session")
def file_removed_diff(flexlate_dev_repo: Repo) -> PatchedFile:
    patch_set = _get_diff_between_commit_and_parent(flexlate_dev_repo, REMOVED_FILE_SHA)
    for patch in patch_set:
        if patch.is_removed_file:
            return patch
    raise ValueError("No removed file found")


@pytest.fixture(scope="session")
def file_renamed_diff(flexlate_dev_repo: Repo) -> PatchedFile:
    patch_set = _get_diff_between_commit_and_parent(flexlate_dev_repo, RENAMED_FILE_SHA)
    for patch in patch_set:
        if patch.is_rename:
            return patch
    raise ValueError("No renamed file found")


@pytest.fixture(scope="session")
def file_modified_diff(flexlate_dev_repo: Repo) -> PatchedFile:
    patch_set = _get_diff_between_commit_and_parent(
        flexlate_dev_repo, MODIFIED_FILE_SHA
    )
    return patch_set[0]
