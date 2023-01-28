import shutil
from pathlib import Path

import pytest
from git import Repo

from flexlate_dev.gitutils import stage_and_commit_all
from tests.config import COPIER_ONE_DIR, GENERATED_FILES_DIR


@pytest.fixture
def copier_one_template_repo(copier_one_template_path: Path) -> Repo:
    path = copier_one_template_path
    repo = Repo.init(path)
    stage_and_commit_all(repo, "Initial commit")
    yield repo
