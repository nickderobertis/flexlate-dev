from flexlate_dev.command_type import CommandType
from flexlate_dev.config import FlexlateDevConfig
from flexlate_dev.project_ops import initialize_project_get_folder, update_project

from tests.fixtures.template_path import *


def test_init_project_creates_project_with_default_data(copier_one_template_path: Path):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig()
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    run_config = config.get_run_config(CommandType.SERVE, None)

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

    # Change the template contents, allowing update
    template_file.write_text("new content {{ q2 }}")

    update_project(project_path, config, run_config, no_input=True)

    assert expect_file.read_text() == "new content 1"
