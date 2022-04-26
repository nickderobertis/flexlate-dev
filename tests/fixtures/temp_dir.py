import pytest

from flexlate_dev.dirutils import change_directory_to
from tests.config import GENERATED_FILES_DIR


@pytest.fixture
def inside_generated_dir():
    with change_directory_to(GENERATED_FILES_DIR):
        yield
