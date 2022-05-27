import os
import shutil
from pathlib import Path

from flexlate_dev.ignore import IgnoreSpecification
from tests.fixtures.temp_dir import inside_generated_dir


def test_ignore_file(inside_generated_dir):
    ignore = IgnoreSpecification(ignore_list=["a.txt"])
    _make_file_and_check_ignore("a.txt", ignore, True)
    _make_file_and_check_ignore("b.txt", ignore, False)


def test_ignore_folder_only(inside_generated_dir):
    ignore = IgnoreSpecification(ignore_list=["a/"])
    _make_file_and_check_ignore("a/b.txt", ignore, True)
    _make_file_and_check_ignore("a/", ignore, True)
    _make_file_and_check_ignore("a", ignore, False, force_file=True)
    _make_file_and_check_ignore("a", ignore, True, force_folder=True)
    _make_file_and_check_ignore("ab", ignore, False)
    _make_file_and_check_ignore("ab/", ignore, False)
    _make_file_and_check_ignore("b.txt", ignore, False)


def test_ignore_folder_or_file(inside_generated_dir):
    ignore = IgnoreSpecification(ignore_list=["a"])
    _make_file_and_check_ignore("a/b.txt", ignore, True)
    _make_file_and_check_ignore("a/", ignore, True)
    _make_file_and_check_ignore("a", ignore, True, force_file=True)
    _make_file_and_check_ignore("a", ignore, True, force_folder=True)
    _make_file_and_check_ignore("ab", ignore, False)
    _make_file_and_check_ignore("ab/", ignore, False)
    _make_file_and_check_ignore("b.txt", ignore, False)


def test_ignore_folder_does_not_ignore_folders_that_start_with_that_name(
    inside_generated_dir,
):
    ignore = IgnoreSpecification(ignore_list=["a/"])
    _make_file_and_check_ignore("a/b.txt", ignore, True)
    _make_file_and_check_ignore("ab/c.txt", ignore, False)


def test_negate_ignore(inside_generated_dir):
    ignore = IgnoreSpecification(ignore_list=["a/", "!a/b.txt"])
    _make_file_and_check_ignore("a/a.txt", ignore, True)
    _make_file_and_check_ignore("a/b.txt", ignore, False)
    _make_file_and_check_ignore("b.txt", ignore, False)


def test_negate_ignore_that_was_previously_ignored(inside_generated_dir):
    ignore = IgnoreSpecification(ignore_list=["a/", "!a/"])
    _make_file_and_check_ignore("a/b.txt", ignore, False)
    _make_file_and_check_ignore("a/a.txt", ignore, False)
    _make_file_and_check_ignore("b.txt", ignore, False)


def test_ignore_glob(inside_generated_dir):
    ignore = IgnoreSpecification(ignore_list=["a/*.txt"])
    _make_file_and_check_ignore("a/a.txt", ignore, True)
    _make_file_and_check_ignore("a/b.txt", ignore, True)
    _make_file_and_check_ignore("a/a.py", ignore, False)
    _make_file_and_check_ignore("b.txt", ignore, False)


def test_empty_ignore_does_not_ignore_anything(inside_generated_dir):
    ignore = IgnoreSpecification(ignore_list=[])
    _make_file_and_check_ignore("a/a.txt", ignore, False)
    _make_file_and_check_ignore("a/b.txt", ignore, False)
    _make_file_and_check_ignore("b.txt", ignore, False)


def _make_file_and_check_ignore(
    file_path: str,
    ignore_spec: IgnoreSpecification,
    expected_result: bool,
    force_file: bool = False,
    force_folder: bool = False,
):
    path = Path(file_path)
    if force_file or (not force_folder and "." in file_path):
        # Got a file, write it
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        remove = lambda: os.remove(path)
    else:
        # Got a folder, create it
        path.mkdir(parents=True, exist_ok=True)
        remove = lambda: shutil.rmtree(path)
    assert ignore_spec.file_is_ignored(file_path) == expected_result
    # Clean up
    remove()
