from pathlib import Path

from flexlate_dev.command_type import CommandType
from flexlate_dev.config import FlexlateDevConfig, DataConfiguration
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
    run_config = config.get_run_config(CommandType.SERVE, None)

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
