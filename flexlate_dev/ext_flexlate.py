from pathlib import Path
from typing import List

from flexlate.config import TemplateSource
from flexlate.config_manager import ConfigManager
from flexlate.exc import CannotParseCommitMessageFlexlateTransaction
from flexlate.ext_git import get_commits_between_two_commits
from flexlate.transactions.transaction import (
    FlexlateTransaction,
    _is_flexlate_merge_commit,
)
from git import Commit, Repo  # type: ignore[attr-defined]
from pydantic import BaseModel


def get_render_relative_root_in_template_from_project_path(project_path: Path) -> Path:
    ts = _get_template_source_from_project_path(project_path)
    return ts.render_relative_root_in_template


def get_template_path_from_project_path(project_path: Path) -> str:
    ts = _get_template_source_from_project_path(project_path)
    return ts.path


def _get_template_source_from_project_path(project_path: Path) -> TemplateSource:
    config_manager = ConfigManager()
    config = config_manager.load_config(project_path)
    if len(config.template_sources) != 1:
        raise ValueError(
            "Must have only a single template source to extract relative root"
        )
    ts = config.template_sources[0]
    return ts


def get_non_flexlate_commits_between_commits(
    repo: Repo,
    start: Commit,
    end: Commit,
    merged_branch_name: str,
    template_branch_name: str,
) -> List[Commit]:
    between_commits = get_commits_between_two_commits(repo, start, end)
    non_flexlate_commits: List[Commit] = []
    for commit in between_commits:
        if _is_flexlate_merge_commit(commit, merged_branch_name, template_branch_name):
            continue
        try:
            FlexlateTransaction.parse_commit_message(commit.message)
        except CannotParseCommitMessageFlexlateTransaction:
            non_flexlate_commits.append(commit)
    return non_flexlate_commits


class FlexlateBranchNames(BaseModel):
    merged_branch_name: str
    template_branch_name: str


def get_flexlate_branch_names_from_project_path(
    project_path: Path,
) -> FlexlateBranchNames:
    config_manager = ConfigManager()
    config = config_manager.load_project_config(project_path)
    return FlexlateBranchNames(
        merged_branch_name=config.merged_branch_name,
        template_branch_name=config.template_branch_name,
    )
