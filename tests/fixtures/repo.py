import pytest
from git import Repo

from tests.config import PROJECT_DIR


@pytest.fixture(scope="session")
def flexlate_dev_repo() -> Repo:
    return Repo(PROJECT_DIR)
