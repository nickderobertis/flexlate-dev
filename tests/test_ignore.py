from flexlate_dev.ignore import IgnoreSpecification
from tests.config import GENERATED_FILES_DIR
from tests.fixtures.temp_dir import inside_generated_dir


def test_ignore_file(inside_generated_dir):
    ignore = IgnoreSpecification(ignore_list=["a.txt"], base_dir=GENERATED_FILES_DIR)
    assert ignore.file_is_ignored("a.txt")
    assert not ignore.file_is_ignored("b.txt")


def test_ignore_folder(inside_generated_dir):
    ignore = IgnoreSpecification(ignore_list=["a/"], base_dir=GENERATED_FILES_DIR)
    b_path = GENERATED_FILES_DIR / "a" / "b.txt"
    assert ignore.file_is_ignored(b_path)
    assert not ignore.file_is_ignored("b.txt")
