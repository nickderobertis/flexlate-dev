from pathlib import Path

import pytest
from flexlate import Flexlate
from git import Repo

from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.config import (
    FlexlateDevConfig,
    UserDataConfiguration,
)
from flexlate_dev.user_runner import UserRootRunConfiguration
from flexlate_dev.gituitls import stage_and_commit_all
from flexlate_dev.project_ops import update_or_initialize_project_get_folder
from tests.fixtures.template_path import *


def test_update_or_init_project_creates_project_when_no_folder_name_in_config(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    config = FlexlateDevConfig()
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    run_config = config.get_full_run_config(ExternalCLICommandType.SERVE, None)

    assert not expect_file.exists()

    update_or_initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=None,
        save=True,
    )

    assert expect_file.read_text() == "1"


def test_update_or_init_project_creates_project_when_path_does_not_exist(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    config = FlexlateDevConfig()
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    data_config = UserDataConfiguration(folder_name="project")
    config.data["default"] = data_config
    run_config = config.get_full_run_config(ExternalCLICommandType.SERVE, None)

    assert not expect_file.exists()

    update_or_initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=None,
        save=True,
    )

    assert expect_file.read_text() == "1"


def test_update_or_init_project_updates_project_when_folder_is_defined_and_path_exists(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig()
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    data_config = UserDataConfiguration(folder_name="project")
    config.data["default"] = data_config
    run_config = config.get_full_run_config(ExternalCLICommandType.SERVE, None)

    assert not expect_file.exists()

    # Directly run fxt to initialize the project
    fxt = Flexlate()
    fxt.init_project_from(
        str(template_path),
        GENERATED_FILES_DIR,
        default_folder_name="project",
        no_input=True,
    )

    # First update should be a no-op as the output file is already up to date
    update_or_initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=None,
        save=True,
    )
    assert expect_file.read_text() == "1"

    # Change the template contents, allowing update
    template_file.write_text("new content {{ q2 }}")

    # Second update should should bring the new content
    update_or_initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=None,
        save=True,
    )

    assert expect_file.read_text() == "new content 1"
