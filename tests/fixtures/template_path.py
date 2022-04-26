import shutil
from pathlib import Path

import pytest

from tests.config import COPIER_ONE_DIR, GENERATED_FILES_DIR


@pytest.fixture
def copier_one_template_path() -> Path:
    orig_path = COPIER_ONE_DIR
    new_path = GENERATED_FILES_DIR / orig_path.name
    shutil.copytree(COPIER_ONE_DIR, new_path)
    yield new_path
