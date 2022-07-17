import time
from pathlib import Path

from git import Repo

from flexlate_dev.config import FlexlateDevConfig, UserDataConfiguration
from flexlate_dev.gitutils import stage_and_commit_all
from flexlate_dev.server.main import run_server
from flexlate_dev.user_runner import UserRunConfiguration
from tests.config import (
    BLOCKING_COMMAND_CONFIG_PATH,
    EXTEND_DEFAULT_RUN_CONFIG_PATH,
    EXTEND_RUN_CONFIG_PATH,
    GENERATED_FILES_DIR,
    IGNORES_AND_EXTEND_DATA_PATH,
    SEPARATE_PUBLISH_SERVE_CONFIG_PATH,
)
from tests.fixtures.template_path import *
from tests.fixtures.template_repo import copier_one_template_repo
from tests.pathutils import change_directory_to
from tests.waitutils import (
    wait_until_file_has_content,
    wait_until_file_updates,
    wait_until_path_exists,
    wait_until_returns_true,
)


def test_server_creates_and_updates_template_on_change(copier_one_template_path: Path):
    template_path = copier_one_template_path
    folder_name = "project"
    project_path = GENERATED_FILES_DIR / folder_name
    expect_file = project_path / "a1.txt"
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
    custom_folder_name = "custom_folder_name"
    project_path = GENERATED_FILES_DIR / custom_folder_name
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config_path = project_path / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    data_config = UserDataConfiguration(data=dict(q2=50))
    config.data["default"] = data_config
    serve_config = UserRunConfiguration(data_name="default")
    config.run_configs["default"].serve = serve_config
    with run_server(
        config,
        None,
        template_path,
        GENERATED_FILES_DIR,
        no_input=True,
        save=True,
        folder_name=custom_folder_name,
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
        data_config = config.data["default"]
        assert data_config.data == dict(q1="a1", q2=50, q3=None)
        assert data_config.folder_name == custom_folder_name


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


@pytest.mark.parametrize(
    "config_path", [EXTEND_RUN_CONFIG_PATH, EXTEND_DEFAULT_RUN_CONFIG_PATH]
)
def test_server_resolves_an_extended_run_config_to_run_commands(
    copier_one_template_path: Path,
    config_path: Path,
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig.load(config_path)
    with run_server(
        config, "my-run-config", template_path, GENERATED_FILES_DIR, no_input=True
    ):
        wait_until_path_exists(expect_file)
        # Check initial load
        assert expect_file.read_text() == "1"
        modified_time = expect_file.lstat().st_mtime

        # Cause a reload
        template_file.write_text("new content {{ q2 }}")

        # Check reload
        wait_until_file_has_content(expect_file, modified_time, "new content 1")

        # Check that it properly extended the config to pick the correct commands
        wait_until_path_exists(project_path / "overridden.txt")
        wait_until_path_exists(project_path / "something_else.txt")
        assert not (project_path / "something.txt").exists()


def test_server_resolves_a_separate_serve_config_to_run_commands(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig.load(SEPARATE_PUBLISH_SERVE_CONFIG_PATH)
    with run_server(
        config, "my-run-config", template_path, GENERATED_FILES_DIR, no_input=True
    ):
        wait_until_path_exists(expect_file)
        # Check initial load
        assert expect_file.read_text() == "1"
        modified_time = expect_file.lstat().st_mtime

        # Cause a reload
        template_file.write_text("new content {{ q2 }}")

        # Check reload
        wait_until_file_has_content(expect_file, modified_time, "new content 1")

        # Check that it properly used the serve key in the config to pick the correct commands
        wait_until_path_exists(project_path / "serve-pre-update.txt")
        wait_until_path_exists(project_path / "serve-post-update.txt")
        wait_until_path_exists(project_path / "post-init.txt")
        assert not (project_path / "overridden.txt").exists()
        assert not (project_path / "base-pre-update.txt").exists()
        assert not (project_path / "base-post-update.txt").exists()
        assert not (project_path / "publish-pre-update.txt").exists()


def test_server_overrides_data_and_folder_name(copier_one_template_path: Path):
    template_path = copier_one_template_path
    folder_name = "custom-folder-name"
    project_path = GENERATED_FILES_DIR / folder_name
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig()
    with run_server(
        config,
        None,
        template_path,
        GENERATED_FILES_DIR,
        no_input=True,
        data=dict(q2=4),
        folder_name=folder_name,
    ):
        wait_until_path_exists(expect_file)
        # Check initial load
        assert expect_file.read_text() == "4"
        modified_time = expect_file.lstat().st_mtime

        # Cause a reload
        template_file.write_text("new content {{ q2 }}")

        # Check reload
        wait_until_file_has_content(expect_file, modified_time, "new content 4")


def test_server_ignores_changes_to_ignored_files(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    project_path = GENERATED_FILES_DIR / "project"
    default_ignored_template_file = template_path / ".git" / "something.txt"
    default_ignored_template_file.parent.mkdir()
    default_ignored_template_file.write_text("initial content")
    default_ignored_expect_file = project_path / ".git" / "something.txt"
    custom_ignored_template_file = template_path / "ignored.txt"
    custom_ignored_template_file.write_text("initial content")
    custom_ignored_expect_file = project_path / "ignored.txt"
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    config = FlexlateDevConfig.load(IGNORES_AND_EXTEND_DATA_PATH)
    with run_server(config, None, template_path, GENERATED_FILES_DIR, no_input=True):
        wait_until_path_exists(expect_file)
        wait_until_path_exists(custom_ignored_expect_file)
        assert not default_ignored_expect_file.exists()
        # Check initial load
        assert expect_file.read_text() == "2"
        assert custom_ignored_expect_file.read_text() == "initial content"

        # Should not reload from a change to the custom or default ignored file
        custom_ignored_template_file.write_text("new content")
        default_ignored_template_file.write_text("new content")

        # TODO: Need a better wait to wait until the server has processed the change, perhaps can expose events from the server
        time.sleep(5)

        # Files should be unchanged
        assert expect_file.read_text() == "2"
        assert not default_ignored_expect_file.exists()
        assert custom_ignored_expect_file.read_text() == "initial content"

        # Cause a reload
        modified_time = expect_file.lstat().st_mtime
        template_file.write_text("new content {{ q2 }}")

        # Check reload
        wait_until_file_has_content(expect_file, modified_time, "new content 2")
        # Should have updated the files that were ignored. Content still updates once they actually do get reloaded.
        # The default ignore is in the .git directory, and so it should never exist.
        assert custom_ignored_expect_file.read_text() == "new content"
        assert not default_ignored_expect_file.exists()


def test_server_back_syncs_changes_from_project_to_template_copier(
    copier_one_template_repo: Repo,
):
    template_path = Path(copier_one_template_repo.working_dir)
    folder_name = "project"
    project_path = GENERATED_FILES_DIR / folder_name
    expect_file = project_path / "a1.txt"
    template_file = template_path / "{{ q1 }}.txt.jinja"
    non_templated_template_file = template_path / "README.md"
    non_templated_expect_file = project_path / "README.md"
    config = FlexlateDevConfig()
    with run_server(
        config, None, template_path, GENERATED_FILES_DIR, no_input=True, back_sync=True
    ) as context:
        project_repo = Repo(project_path)

        wait_until_path_exists(expect_file)
        # Check initial load
        assert expect_file.read_text() == "1"
        templated_modified_time = expect_file.lstat().st_mtime
        assert non_templated_expect_file.read_text() == "some existing content"
        assert non_templated_template_file.read_text() == "some existing content"
        non_templated_modified_time = non_templated_template_file.lstat().st_mtime

        # Cause a back sync
        non_templated_expect_file.write_text("new content")
        stage_and_commit_all(project_repo, "Trigger back sync")

        # Check back sync
        wait_until_file_has_content(
            # After fixing the TODO about adding new lines, set this back to "new content"
            non_templated_template_file,
            non_templated_modified_time,
            "new content\n",
        )

        wait_until_returns_true(
            lambda: not context.is_back_syncing, "Back sync is still running"
        )

        # Cause a reload
        template_file.write_text("new content {{ q2 }}")

        # Check reload
        wait_until_file_has_content(
            expect_file, templated_modified_time, "new content 1"
        )


# TODO: add tests for back sync cookiecutter
# TODO: add tests for auto-commit, need to set up temp git repos
