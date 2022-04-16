from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.config import FlexlateDevConfig
from flexlate_dev.user_runner import UserRunConfiguration
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

    # Change the template contents, allowing update
    template_file.write_text("new content {{ q2 }}")

    update_project(project_path, config, run_config, no_input=True)

    assert expect_file.read_text() == "new content 1"


def test_init_project_runs_pre_and_post_update(copier_one_template_path: Path):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config_path = project_path / "flexlate-dev.yaml"
    extra_file = project_path / "extra.txt"
    config = FlexlateDevConfig.load_or_create(config_path)
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    user_run_config = UserRunConfiguration(
        pre_update=[f"echo $(date +%N) > {extra_file}"],
        post_update=[f"echo $(date +%N) >> {extra_file}"],
    )
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
    )

    assert expect_file.read_text() == "1"

    # Change the template contents, allowing update
    template_file.write_text("new content {{ q2 }}")

    update_project(project_path, config, run_config, no_input=True)

    assert expect_file.read_text() == "new content 1"

    # Check that there are two different dates in the file
    lines = extra_file.read_text().splitlines()
    assert len(lines) == 2
    assert lines[0] != lines[1]
