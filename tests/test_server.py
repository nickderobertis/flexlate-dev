from pathlib import Path

from flexlate_dev.config import FlexlateDevConfig, DataConfiguration
from flexlate_dev.server import run_server
from tests.config import GENERATED_FILES_DIR, BLOCKING_COMMAND_CONFIG_PATH
from tests.pathutils import change_directory_to
from tests.waitutils import (
    wait_until_path_exists,
    wait_until_file_updates,
    wait_until_file_has_content,
)
from tests.fixtures.template_path import *


def test_server_creates_and_updates_template_on_change(copier_one_template_path: Path):
    template_path = copier_one_template_path
    expect_file = GENERATED_FILES_DIR / "project" / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig()
    with run_server(config, None, template_path, GENERATED_FILES_DIR, no_input=True):
        wait_until_path_exists(expect_file)
        # Check initial load
        assert expect_file.read_text() == "1"
        modified_time = expect_file.lstat().st_mtime

        # Cause a reload
        template_file.write_text("new content {{ q2 }}")

        # Check reload
        wait_until_file_has_content(expect_file, modified_time, "new content 1")


def test_server_from_current_directory_creates_and_updates_template_on_change(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    config = FlexlateDevConfig()
    with change_directory_to(template_path):
        expect_file = GENERATED_FILES_DIR / "project" / "a1.txt"
        template_file = Path("{{ q1 }}.txt.jinja")
        with run_server(config, out_path=GENERATED_FILES_DIR, no_input=True):
            wait_until_path_exists(expect_file)
            # Check initial load
            assert expect_file.read_text() == "1"
            modified_time = expect_file.lstat().st_mtime

            # Cause a reload
            template_file.write_text("new content {{ q2 }}")

            # Check reload
            wait_until_file_has_content(expect_file, modified_time, "new content 1")


def test_server_creates_and_updates_template_on_change_after_generated_project_changes(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    generated_project_path = GENERATED_FILES_DIR / "project"
    expect_file = generated_project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig()
    with run_server(config, None, template_path, GENERATED_FILES_DIR, no_input=True):
        wait_until_path_exists(expect_file)
        # Check initial load
        assert expect_file.read_text() == "1"
        modified_time = expect_file.lstat().st_mtime

        # Modify files in the project
        generated_modify_path = generated_project_path / "README.md"
        new_content = "new content for README"
        generated_modify_path.write_text(new_content)

        # Cause a reload
        template_file.write_text("new content {{ q2 }}")

        # Check reload
        wait_until_file_has_content(expect_file, modified_time, "new content 1")

        # Check modified file
        assert generated_modify_path.read_text() == new_content


def test_server_creates_project_with_config_data(copier_one_template_path: Path):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config_path = project_path / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    data_config = DataConfiguration(data=dict(q2=50))
    config.data["default"] = data_config
    config.run_configs["default_serve"].data_name = "default"
    with run_server(
        config, None, template_path, GENERATED_FILES_DIR, no_input=True, save=True
    ):
        wait_until_path_exists(expect_file)
        # Check initial load
        assert expect_file.read_text() == "50"
        modified_time = expect_file.lstat().st_mtime

        # Cause a reload
        template_file.write_text("new content {{ q2 }}")

        # Check reload
        wait_until_file_has_content(expect_file, modified_time, "new content 50")

        # Check that config was saved
        config = FlexlateDevConfig.load(config_path)
        assert config.data["default"].data == dict(q1="a1", q2=50, q3=None)


def test_server_runs_a_background_command_and_keeps_reloading(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    expect_file = GENERATED_FILES_DIR / "project" / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig.load(BLOCKING_COMMAND_CONFIG_PATH)
    with run_server(config, None, template_path, GENERATED_FILES_DIR, no_input=True):
        wait_until_path_exists(expect_file)
        # Check initial load
        assert expect_file.read_text() == "1"
        modified_time = expect_file.lstat().st_mtime

        # Cause a reload
        template_file.write_text("new content {{ q2 }}")

        # Check reload
        wait_until_file_has_content(expect_file, modified_time, "new content 1")
