from pathlib import Path

from git import Repo

from flexlate_dev.config import (
    FlexlateDevConfig,
    DataConfiguration,
)
from flexlate_dev.user_runner import UserRunConfiguration
from flexlate_dev.gituitls import stage_and_commit_all
from flexlate_dev.publish import publish_template
from flexlate_dev.server import run_server
from tests.config import GENERATED_FILES_DIR
from tests.pathutils import change_directory_to
from tests.fixtures.template_path import *
from tests.test_config import WITH_USER_COMMAND_CONFIG_PATH


def test_publish_creates_output(copier_one_template_path: Path):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"

    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    run_config = UserRunConfiguration(
        post_init=["touch one.txt"], post_update=["touch two.txt"]
    )
    config.run_configs["default_publish"] = run_config
    config.save()

    assert not expect_file.exists()
    publish_template(
        template_path, GENERATED_FILES_DIR, config_path=config_path, no_input=True
    )
    assert expect_file.read_text() == "1"

    # Check that post init but not post update was run
    assert (project_path / "one.txt").exists()
    assert not (project_path / "two.txt").exists()


def test_publish_updates_existing_output(copier_one_template_path: Path):
    template_path = copier_one_template_path
    template_file = template_path / "{{ q1 }}.txt.jinja"
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"

    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    run_config = UserRunConfiguration(
        post_init=["touch one.txt"], post_update=["touch two.txt"]
    )
    config.run_configs["default_publish"] = run_config
    config.save()

    # Do a first publish so that project exists
    assert not expect_file.exists()
    publish_template(
        template_path,
        GENERATED_FILES_DIR,
        config_path=config_path,
        no_input=True,
        save=True,
    )
    assert expect_file.read_text() == "1"

    # Check that post init but not post update was run
    assert (project_path / "one.txt").exists()
    assert not (project_path / "two.txt").exists()

    # Commit to get a clean slate for next update
    repo = Repo(project_path)
    stage_and_commit_all(repo, "Add one.txt")

    # Update the template
    template_file.write_text("new content {{ q2 }}")

    # Publish again, should do update
    publish_template(
        template_path, GENERATED_FILES_DIR, config_path=config_path, no_input=True
    )

    # Check that output was updated
    assert expect_file.read_text() == "new content 1"

    # Check that post update was run
    assert (project_path / "two.txt").exists()


def test_publish_updates_existing_output_from_template_path_with_publish_up_one_level(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    template_file = template_path / "{{ q1 }}.txt.jinja"
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"

    config_path = template_path / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    run_config = UserRunConfiguration(
        post_init=["touch one.txt"], post_update=["touch two.txt"]
    )
    config.run_configs["default_publish"] = run_config
    config.save()

    # Do a first publish so that project exists
    assert not expect_file.exists()

    with change_directory_to(template_path):
        publish_template(
            Path("."),
            Path(".."),
            config_path=config_path,
            no_input=True,
            save=True,
        )
        assert expect_file.read_text() == "1"

        # Check that post init but not post update was run
        assert (project_path / "one.txt").exists()
        assert not (project_path / "two.txt").exists()

        # Commit to get a clean slate for next update
        repo = Repo(project_path)
        stage_and_commit_all(repo, "Add one.txt")

        # Update the template
        template_file.write_text("new content {{ q2 }}")

        # Publish again, should do update
        publish_template(Path("."), Path(".."), config_path=config_path, no_input=True)

    # Check that output was updated
    assert expect_file.read_text() == "new content 1"

    # Check that post update was run
    assert (project_path / "two.txt").exists()


def test_publish_runs_user_commands_from_config_file(copier_one_template_path: Path):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"

    assert not expect_file.exists()
    publish_template(
        template_path,
        GENERATED_FILES_DIR,
        run_config_name="my-run-config",
        config_path=WITH_USER_COMMAND_CONFIG_PATH,
        no_input=True,
    )
    assert expect_file.read_text() == "1"

    # Check that post init (both inline and referenced) but not post update was run
    assert (project_path / "user_command.txt").exists()
    assert (project_path / "referenced.txt").exists()
    assert not (project_path / "string_command.txt").exists()
