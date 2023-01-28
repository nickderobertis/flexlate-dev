import contextlib
from typing import Iterator, List

from git import Commit, Repo  # type: ignore[attr-defined]
from pydantic import BaseModel


def stage_and_commit_all(repo: Repo, commit_message: str):
    repo.git.add("-A")
    repo.git.commit("-m", commit_message)


def create_branch_from_commits_get_new_shas(
    repo: Repo, branch_name: str, base_commit: Commit, commits: List[Commit]
) -> List[str]:
    repo.git.checkout(base_commit, b=branch_name)
    new_shas: List[str] = []
    for commit in commits:
        repo.git.cherry_pick(commit.hexsha)
        new_shas.append(repo.head.commit.hexsha)
    return new_shas


class BranchInfo(BaseModel):
    name: str
    commit_shas: List[str]


@contextlib.contextmanager
def temporary_branch_from_commits(
    repo: Repo, base_commit: Commit, commits: List[Commit]
) -> Iterator[BranchInfo]:
    current_branch = repo.active_branch.name
    branch_name = "-".join(["temp", *[commit.hexsha for commit in commits]])
    new_shas = create_branch_from_commits_get_new_shas(
        repo, branch_name, base_commit, commits
    )
    repo.git.checkout(current_branch)
    yield BranchInfo(name=branch_name, commit_shas=new_shas)
    # Delete the created branch
    repo.git.branch(branch_name, D=True)
