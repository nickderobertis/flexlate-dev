from pathlib import Path

from flexlate_dev.server import run_server
from tests.config import GENERATED_FILES_DIR
from tests.fixtures.template_path import copier_one_template_path
from tests.pathutils import change_directory_to
from tests.waitutils import wait_until_path_exists, wait_until_file_updates


def test_server_creates_and_updates_template_on_change(copier_one_template_path: Path):
    template_path = copier_one_template_path
    expect_file = GENERATED_FILES_DIR / "project" / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    with run_server(template_path, GENERATED_FILES_DIR, no_input=True):
        wait_until_path_exists(expect_file)
        # Check initial load
        assert expect_file.read_text() == "1"
        modified_time = expect_file.lstat().st_mtime

        # Cause a reload
        template_file.write_text("new content {{ q2 }}")

        # Check reload
        wait_until_file_updates(expect_file, modified_time)
        assert expect_file.read_text() == "new content 1"


def test_server_from_current_directory_creates_and_updates_template_on_change(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    with change_directory_to(template_path):
        expect_file = GENERATED_FILES_DIR / "project" / "a1.txt"
        template_file = Path("{{ q1 }}.txt.jinja")
        with run_server(out_path=GENERATED_FILES_DIR, no_input=True):
            wait_until_path_exists(expect_file)
            # Check initial load
            assert expect_file.read_text() == "1"
            modified_time = expect_file.lstat().st_mtime

            # Cause a reload
            template_file.write_text("new content {{ q2 }}")

            # Check reload
            wait_until_file_updates(expect_file, modified_time)
            assert expect_file.read_text() == "new content 1"
