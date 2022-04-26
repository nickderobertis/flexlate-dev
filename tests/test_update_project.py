from unittest.mock import patch

import jinja2
from flexlate import branch_update
from git import Repo

from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.config import FlexlateDevConfig
from flexlate_dev.user_runner import UserRootRunConfiguration, UserRunConfiguration
from flexlate_dev.project_ops import initialize_project_get_folder, update_project

from tests.fixtures.template_path import *
from tests.fixtures.jinja_env import jinja_env


def test_update_project_updates_project_with_default_data(
    copier_one_template_path: Path, jinja_env: jinja2.Environment
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig()
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    run_config = config.get_full_run_config(ExternalCLICommandType.SERVE, None)

    initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=None,
        save=True,
        jinja_env=jinja_env,
    )

    assert expect_file.read_text() == "1"

    # Change the template contents, allowing update
    template_file.write_text("new content {{ q2 }}")

    update_project(project_path, config, run_config, no_input=True, jinja_env=jinja_env)

    assert expect_file.read_text() == "new content 1"


def test_update_project_runs_pre_and_post_update(
    copier_one_template_path: Path, jinja_env: jinja2.Environment
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config_path = project_path / "flexlate-dev.yaml"
    extra_file = project_path / "extra.txt"
    config = FlexlateDevConfig.load_or_create(config_path)
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    serve_config = UserRunConfiguration(
        pre_update=[f"echo $(date +%N) > {extra_file}"],
        post_update=[f"echo $(date +%N) >> {extra_file}"],
    )
    user_run_config = UserRootRunConfiguration(
        serve=serve_config,
    )
    config.run_configs["default"] = user_run_config
    run_config = config.get_full_run_config(ExternalCLICommandType.SERVE, None)

    initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=None,
        save=True,
        jinja_env=jinja_env,
    )

    assert expect_file.read_text() == "1"

    # Change the template contents, allowing update
    template_file.write_text("new content {{ q2 }}")

    update_project(project_path, config, run_config, no_input=True, jinja_env=jinja_env)

    assert expect_file.read_text() == "new content 1"

    # Check that there are two different dates in the file
    lines = extra_file.read_text().splitlines()
    assert len(lines) == 2
    assert lines[0] != lines[1]


def test_update_project_auto_commits_with_correct_message(
    copier_one_template_path: Path, jinja_env: jinja2.Environment
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig()
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    run_config = config.get_full_run_config(ExternalCLICommandType.SERVE, None)

    initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=None,
        save=True,
        jinja_env=jinja_env,
    )

    repo = Repo(project_path)

    def _assert_last_non_merge_commit_message_matches(message: str):
        assert repo.commit().parents[0].message == f"{message}\n"

    assert expect_file.read_text() == "1"

    # Change the template contents, allowing update
    template_file.write_text("new content {{ q2 }}")

    # Make a change in the generated project, forcing it to auto-commit
    temp_path = project_path / "temp.txt"
    temp_path.touch()

    update_project(project_path, config, run_config, no_input=True, jinja_env=jinja_env)

    # Check for default message
    _assert_last_non_merge_commit_message_matches("chore: auto-commit manual changes")

    # Ensure update was successful
    assert expect_file.read_text() == "new content 1"

    # Update the auto-commit message
    expect_commit_message = "expect commit message"
    run_config.config.auto_commit_message = expect_commit_message

    # Change template contents again, allowing a second update
    template_file.write_text("second new content {{ q2 }}")

    # Make another change in the generated project, forcing it to auto-commit
    temp_path = project_path / "temp2.txt"
    temp_path.touch()

    update_project(project_path, config, run_config, no_input=True, jinja_env=jinja_env)

    # Check for custom message
    _assert_last_non_merge_commit_message_matches(expect_commit_message)


def test_update_project_does_not_run_post_update_on_conflict_abort(
    copier_one_template_path: Path, jinja_env: jinja2.Environment
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config_path = project_path / "flexlate-dev.yaml"
    extra_file = project_path / "extra.txt"
    config = FlexlateDevConfig.load_or_create(config_path)
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.settings.config_name = "flexlate-dev"
    serve_run_config = UserRunConfiguration(
        pre_update=[f"echo $(date +%N) > {extra_file}"],
        post_update=[f"echo $(date +%N) >> {extra_file}"],
    )
    user_run_config = UserRootRunConfiguration(serve=serve_run_config)
    config.run_configs["default"] = user_run_config
    run_config = config.get_full_run_config(ExternalCLICommandType.SERVE, None)

    def _reject_update(prompt: str) -> bool:
        return False

    initialize_project_get_folder(
        template_path,
        GENERATED_FILES_DIR,
        config,
        run_config=run_config,
        no_input=True,
        data=None,
        save=True,
        jinja_env=jinja_env,
    )

    assert expect_file.read_text() == "1"

    # Change the template contents, allowing update
    template_file.write_text("new content {{ q2 }}")

    # Change the output file, causing a conflict
    expect_file.write_text("2")

    with patch.object(branch_update, "confirm_user", _reject_update):
        update_project(
            project_path, config, run_config, no_input=True, jinja_env=jinja_env
        )

    # Check that update was skipped
    assert expect_file.read_text() == "2"

    # Check that only pre-update was run, so there is a single date in the file
    lines = extra_file.read_text().splitlines()
    assert len(lines) == 1
