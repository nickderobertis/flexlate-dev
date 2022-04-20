from pathlib import Path

from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.config import (
    FlexlateDevConfig,
    DataConfiguration,
)
from flexlate_dev.user_runner import UserRunConfiguration
from flexlate_dev.project_ops import initialize_project_get_folder
from tests.fixtures.template_path import *


def test_init_project_creates_project_with_data(copier_one_template_path: Path):
    template_path = copier_one_template_path
    custom_folder_name = "custom_folder_name"
    project_path = GENERATED_FILES_DIR / custom_folder_name
    expect_file = project_path / "a1.txt"
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    data_config = DataConfiguration(data=dict(q2=50))
    config.data["default"] = data_config
    config.run_configs["default_serve"].data_name = "default"
    run_config = config.get_run_config(ExternalCLICommandType.SERVE, None)

    folder = initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=run_config.data.data,
        save=True,
        default_folder_name=custom_folder_name,
    )

    assert folder == custom_folder_name
    assert expect_file.read_text() == "50"

    # Check that config was saved
    loaded_config = FlexlateDevConfig.load(config_path)
    assert loaded_config.data["default"].data == dict(q1="a1", q2=50, q3=None)


def test_init_project_creates_project_with_default_data(copier_one_template_path: Path):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    config = FlexlateDevConfig()
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    run_config = config.get_run_config(ExternalCLICommandType.SERVE, None)

    initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=None,
        save=True,
    )

    assert expect_file.read_text() == "1"

    # Check that config was saved
    loaded_config = FlexlateDevConfig.load(config_path)
    assert loaded_config.data["default"].data == dict(q1="a1", q2=1, q3=None)


def test_init_project_runs_post_init_after_creating_project(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    custom_folder_name = "custom_folder_name"
    project_path = GENERATED_FILES_DIR / custom_folder_name
    expect_file = project_path / "a1.txt"
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    touch_file_name = "myfile.txt"
    touch_file_path = project_path / touch_file_name
    user_run_config = UserRunConfiguration(post_init=[f"touch {touch_file_name}"])
    config.run_configs["default_serve"] = user_run_config
    run_config = config.get_run_config(ExternalCLICommandType.SERVE, None)

    initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=None,
        save=True,
        default_folder_name=custom_folder_name,
    )

    assert expect_file.read_text() == "1"
    assert touch_file_path.exists()

    # Check that config was saved
    loaded_config = FlexlateDevConfig.load(config_path)
    assert loaded_config.data["default"].data == dict(q1="a1", q2=1, q3=None)
