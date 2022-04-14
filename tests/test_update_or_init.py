from pathlib import Path

from flexlate_dev.command_type import CommandType
from flexlate_dev.config import (
    FlexlateDevConfig,
    DataConfiguration,
    UserRunConfiguration,
)
from flexlate_dev.project_ops import update_or_initialize_project_get_folder
from tests.fixtures.template_path import *


def test_init_project_creates_project_when_no_folder_name_in_config(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    config = FlexlateDevConfig()
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    run_config = config.get_run_config(CommandType.SERVE, None)

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
