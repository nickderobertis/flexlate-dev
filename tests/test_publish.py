from pathlib import Path

from git import Repo

from flexlate_dev.config import (
    FlexlateDevConfig,
    DataConfiguration,
    UserDataConfiguration,
)
from flexlate_dev.user_runner import UserRootRunConfiguration, UserRunConfiguration
from flexlate_dev.gituitls import stage_and_commit_all
from flexlate_dev.publish import publish_template
from flexlate_dev.server import run_server
from tests.config import (
    GENERATED_FILES_DIR,
    SEPARATE_PUBLISH_SERVE_CONFIG_PATH,
    WITH_TEMPLATED_COMMANDS_CONFIG_PATH,
    WITH_PRE_CHECK_COMMAND_CONFIG_PATH,
    WITH_PRE_CHECK_CREATE_COMMAND_CONFIG_PATH,
)
from tests.pathutils import change_directory_to
from tests.fixtures.template_path import *
from tests.test_config import WITH_USER_COMMAND_CONFIG_PATH


def test_publish_creates_output(copier_one_template_path: Path):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"

    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    publish_run_config = UserRunConfiguration(
        post_init=["touch one.txt"], post_update=["touch two.txt"]
    )
    run_config = UserRootRunConfiguration(publish=publish_run_config)
    config.run_configs["default"] = run_config
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
    publish_run_config = UserRunConfiguration(
        post_init=["touch one.txt"], post_update=["touch two.txt"]
    )
    run_config = UserRootRunConfiguration(publish=publish_run_config)
    config.run_configs["default"] = run_config
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
    publish_run_config = UserRunConfiguration(
        post_init=["touch one.txt"], post_update=["touch two.txt"]
    )
    run_config = UserRootRunConfiguration(publish=publish_run_config)
    config.run_configs["default"] = run_config
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


def test_publish_runs_user_commands_from_separate_publish_config(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    template_file = template_path / "{{ q1 }}.txt.jinja"
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    shutil.copy(SEPARATE_PUBLISH_SERVE_CONFIG_PATH, config_path)

    assert not expect_file.exists()
    publish_template(
        template_path,
        GENERATED_FILES_DIR,
        run_config_name="my-run-config",
        config_path=config_path,
        no_input=True,
        save=True,
    )
    assert expect_file.read_text() == "1"

    # Check that it properly used the publish key in the config to pick the correct commands
    assert (project_path / "publish-post-init.txt").exists()
    assert not (project_path / "serve-pre-update.txt").exists()
    assert not (project_path / "serve-post-update.txt").exists()
    assert not (project_path / "base-pre-update.txt").exists()
    assert not (project_path / "publish-pre-update.txt").exists()

    # Commit to get a clean slate for next update
    repo = Repo(project_path)
    stage_and_commit_all(repo, "Add publish-post-init.txt")

    # Update the template
    template_file.write_text("new content {{ q2 }}")

    # Publish again, should do update
    publish_template(
        template_path,
        GENERATED_FILES_DIR,
        run_config_name="my-run-config",
        config_path=config_path,
        no_input=True,
    )

    # Check that output was updated
    assert expect_file.read_text() == "new content 1"

    # Check that post update was run
    assert (project_path / "overridden.txt").exists()
    assert (project_path / "base-post-update.txt").exists()
    assert not (project_path / "serve-pre-update.txt").exists()
    assert not (project_path / "serve-post-update.txt").exists()
    assert not (project_path / "base-pre-update.txt").exists()
    assert not (project_path / "publish-pre-update.txt").exists()


def test_publish_creates_output_with_templated_commands(copier_one_template_path: Path):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "a"
    expect_file = project_path / "a1.txt"
    config_path = WITH_TEMPLATED_COMMANDS_CONFIG_PATH

    assert not expect_file.exists()
    publish_template(
        template_path,
        GENERATED_FILES_DIR,
        run_config_name="my-run-config",
        config_path=config_path,
        no_input=True,
    )
    assert expect_file.read_text() == "2"

    # Check that templated command works with post init
    assert (project_path / "2.txt").exists()
    assert (project_path / "my-data.txt").exists()


def test_publish_pre_check_can_alter_whether_init_or_update(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    shutil.copy(WITH_PRE_CHECK_COMMAND_CONFIG_PATH, config_path)

    # On first publish, there is no folder name defined, so it will bypass check and run init
    # Set save=True so it will save the folder name into the config
    assert not expect_file.exists()
    publish_template(
        template_path,
        GENERATED_FILES_DIR,
        run_config_name="my-run-config",
        config_path=config_path,
        no_input=True,
        save=True,
    )
    assert expect_file.read_text() == "1"
    assert (project_path / "post-init.txt").exists()
    assert not (project_path / "post-update.txt").exists()

    # On second publish, project exists and folder name is defined. Normally it would do an update,
    # but the pre-check command will remove the project, causing it to do another init.
    publish_template(
        template_path,
        GENERATED_FILES_DIR,
        run_config_name="my-run-config",
        config_path=config_path,
        no_input=True,
        save=True,
    )
    assert expect_file.read_text() == "1"
    assert (project_path / "post-init.txt").exists()
    assert not (project_path / "post-update.txt").exists()


def test_publish_pre_check_can_make_first_operation_an_update(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "a"
    expect_file = project_path / "a1.txt"
    config_path = WITH_PRE_CHECK_CREATE_COMMAND_CONFIG_PATH

    # On first publish, there is a folder name defined but no folder exists, so it will
    # create the folder and then run check in the folder. This check command then sets up
    # the project to make it run an update rather than an init.
    assert not expect_file.exists()
    publish_template(
        template_path,
        GENERATED_FILES_DIR,
        run_config_name="my-run-config",
        config_path=config_path,
        no_input=True,
    )
    assert expect_file.read_text() == "1"
    assert not (project_path / "post-init.txt").exists()
    assert (project_path / "pre-update.txt").exists()


def test_publish_overrides_data_and_folder_name_from_config(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    custom_folder_name = "custom-folder-name"
    project_path = GENERATED_FILES_DIR / custom_folder_name
    expect_file = project_path / "a1.txt"

    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    data_config = UserDataConfiguration(data=dict(q2=3), folder_name="not-used")
    config.data["my-data"] = data_config
    publish_run_config = UserRunConfiguration(
        post_init=["touch one.txt"], post_update=["touch two.txt"], data_name="my-data"
    )
    run_config = UserRootRunConfiguration(publish=publish_run_config)
    config.run_configs["default"] = run_config
    config.save()

    assert not expect_file.exists()
    publish_template(
        template_path,
        GENERATED_FILES_DIR,
        config_path=config_path,
        no_input=True,
        data=dict(q2=2),
        folder_name=custom_folder_name,
    )
    assert expect_file.read_text() == "2"

    # Check that post init but not post update was run
    assert (project_path / "one.txt").exists()
    assert not (project_path / "two.txt").exists()
