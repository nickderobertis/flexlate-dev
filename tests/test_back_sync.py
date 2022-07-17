from unidiff import PatchedFile

from flexlate_dev.server.back_sync import apply_file_diff_to_project
from tests.config import (
    GENERATED_FILES_DIR,
    MODIFIED_FILE,
    RENAMED_AND_MODIFIED_FILE,
    RENAMED_FILE,
)
from tests.fixtures.diff import (
    file_added_diff,
    file_modified_diff,
    file_removed_diff,
    file_renamed_and_modified_diff,
    file_renamed_diff,
)
from tests.fixtures.repo import flexlate_dev_repo
from tests.fixtures.temp_dir import inside_generated_dir


def test_apply_added_file_diff_to_project(
    file_added_diff: PatchedFile, inside_generated_dir: None
):
    out_dir = GENERATED_FILES_DIR
    expect_file = "setup.cfg"
    expect_path = out_dir / expect_file
    apply_file_diff_to_project(out_dir, file_added_diff)

    assert expect_path.exists()
    assert expect_path.read_text() == "[metadata]\nversion = 0.17.1\n"
    # TODO: check that the file is correct


def test_apply_removed_file_diff_to_project(
    file_removed_diff: PatchedFile, inside_generated_dir: None
):
    out_dir = GENERATED_FILES_DIR
    expect_path = out_dir / "docsrc" / "source" / "_static" / "custom.css"
    expect_path.parent.mkdir(parents=True, exist_ok=True)
    expect_path.touch()
    apply_file_diff_to_project(out_dir, file_removed_diff)

    assert not expect_path.exists()


def test_apply_renamed_file_diff_to_project(
    file_renamed_diff, inside_generated_dir: None
):
    out_dir = GENERATED_FILES_DIR
    common_path = out_dir / "flexlate_dev"
    orig_path = common_path / "gituitls.py"
    moved_to_path = common_path / "gitutils.py"
    orig_file_content = RENAMED_FILE.read_text()
    orig_path.parent.mkdir(parents=True, exist_ok=True)
    orig_path.write_text(orig_file_content)
    assert not moved_to_path.exists()

    apply_file_diff_to_project(out_dir, file_renamed_diff)

    assert not orig_path.exists()
    assert moved_to_path.exists()


def test_apply_renamed_and_modified_file_diff_to_project(
    file_renamed_and_modified_diff, inside_generated_dir: None
):
    out_dir = GENERATED_FILES_DIR
    common_path = out_dir / "flexlate_dev"
    orig_path = common_path / "server.py"
    moved_to_path = common_path / "server" / "sync.py"
    orig_path.parent.mkdir(parents=True, exist_ok=True)
    orig_file_content = RENAMED_AND_MODIFIED_FILE.read_text()
    orig_path.write_text(orig_file_content)
    assert not moved_to_path.exists()

    apply_file_diff_to_project(out_dir, file_renamed_and_modified_diff)

    assert not orig_path.exists()
    assert moved_to_path.exists()

    # Check that the file was also modified
    assert "def serve_template" not in moved_to_path.read_text()


def test_apply_modified_file_diff_to_project(
    file_modified_diff: PatchedFile, inside_generated_dir: None
):
    out_dir = GENERATED_FILES_DIR
    expect_file = "setup.cfg"
    expect_path = out_dir / expect_file
    orig_file_content = MODIFIED_FILE.read_text()
    expect_path.parent.mkdir(parents=True, exist_ok=True)
    expect_path.write_text(orig_file_content)
    assert "0.20.0" not in orig_file_content

    apply_file_diff_to_project(out_dir, file_modified_diff)

    assert expect_path.exists()
    new_file_content = expect_path.read_text()
    assert new_file_content != orig_file_content
    assert "0.20.0" in new_file_content
