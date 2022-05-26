from flexlate_dev.config import FlexlateDevConfig, UserDataConfiguration
from flexlate_dev.publish import publish_all_templates
from flexlate_dev.user_runner import UserRunConfiguration, UserRootRunConfiguration
from tests.config import GENERATED_FILES_DIR
from tests.fixtures.template_path import *


def test_publish_all_creates_output_for_all_run_configurations(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    _create_config_with_default_and_two_run_configs()

    publish_all_templates(
        template_path,
        GENERATED_FILES_DIR,
        config_path=config_path,
        no_input=True,
        always_include_default=True,
    )

    folder_names = ["default", "out-one", "out-two"]
    for folder_name in folder_names:
        project_path = GENERATED_FILES_DIR / folder_name
        expect_file = project_path / "a1.txt"
        assert expect_file.read_text() == "1"
        # Check that post init but not post update was run
        assert (project_path / f"{folder_name}-one.txt").exists()
        assert not (project_path / f"{folder_name}-two.txt").exists()


def test_publish_all_creates_output_for_all_run_configurations_except_default(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    _create_config_with_default_and_two_run_configs()

    publish_all_templates(
        template_path, GENERATED_FILES_DIR, config_path=config_path, no_input=True
    )

    folder_names = ["out-one", "out-two"]
    for folder_name in folder_names:
        project_path = GENERATED_FILES_DIR / folder_name
        expect_file = project_path / "a1.txt"
        assert expect_file.read_text() == "1"
        # Check that post init but not post update was run
        assert (project_path / f"{folder_name}-one.txt").exists()
        assert not (project_path / f"{folder_name}-two.txt").exists()

    # Check that the default project was not created
    not_created_folder_names = ["default"]
    for folder_name in not_created_folder_names:
        project_path = GENERATED_FILES_DIR / folder_name
        expect_file = project_path / "a1.txt"
        assert not expect_file.exists()
        assert not (project_path / f"{folder_name}-one.txt").exists()


def test_publish_all_creates_output_for_all_run_configurations_except_excluded(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    _create_config_with_default_and_two_run_configs()

    publish_all_templates(
        template_path,
        GENERATED_FILES_DIR,
        config_path=config_path,
        no_input=True,
        exclude=["one"],
    )

    folder_names = ["out-two"]
    for folder_name in folder_names:
        project_path = GENERATED_FILES_DIR / folder_name
        expect_file = project_path / "a1.txt"
        assert expect_file.read_text() == "1"
        # Check that post init but not post update was run
        assert (project_path / f"{folder_name}-one.txt").exists()
        assert not (project_path / f"{folder_name}-two.txt").exists()

    # Check that the default project was not created
    not_created_folder_names = ["out-one", "default"]
    for folder_name in not_created_folder_names:
        project_path = GENERATED_FILES_DIR / folder_name
        expect_file = project_path / "a1.txt"
        assert not expect_file.exists()
        assert not (project_path / f"{folder_name}-one.txt").exists()


def test_publish_all_creates_output_for_default_run_configuration_when_it_is_only_one_defined(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    default_publish_run_config = UserRunConfiguration(
        post_init=["touch default-one.txt"],
        post_update=["touch default-two.txt"],
        data_name="default",
    )
    default_data_config = UserDataConfiguration(folder_name="default")
    default_run_config = UserRootRunConfiguration(publish=default_publish_run_config)
    config.run_configs["default"] = default_run_config
    config.data["default"] = default_data_config
    config.save()

    publish_all_templates(
        template_path, GENERATED_FILES_DIR, config_path=config_path, no_input=True
    )

    folder_names = ["default"]
    for folder_name in folder_names:
        project_path = GENERATED_FILES_DIR / folder_name
        expect_file = project_path / "a1.txt"
        assert expect_file.read_text() == "1"
        # Check that post init but not post update was run
        assert (project_path / f"{folder_name}-one.txt").exists()
        assert not (project_path / f"{folder_name}-two.txt").exists()


def _create_config_with_default_and_two_run_configs():
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    config = FlexlateDevConfig.load_or_create(config_path)
    default_publish_run_config = UserRunConfiguration(
        post_init=["touch default-one.txt"],
        post_update=["touch default-two.txt"],
        data_name="default",
    )
    default_data_config = UserDataConfiguration(folder_name="default")
    default_run_config = UserRootRunConfiguration(publish=default_publish_run_config)
    config.run_configs["default"] = default_run_config
    config.data["default"] = default_data_config
    one_publish_run_config = UserRunConfiguration(
        post_init=["touch out-one-one.txt"],
        post_update=["touch out-one-two.txt"],
        data_name="one",
    )
    one_data_config = UserDataConfiguration(folder_name="out-one")
    one_run_config = UserRootRunConfiguration(publish=one_publish_run_config)
    config.run_configs["one"] = one_run_config
    config.data["one"] = one_data_config
    two_publish_run_config = UserRunConfiguration(
        post_init=["touch out-two-one.txt"],
        post_update=["touch out-two-two.txt"],
        data_name="two",
    )
    two_data_config = UserDataConfiguration(folder_name="out-two")
    two_run_config = UserRootRunConfiguration(publish=two_publish_run_config)
    config.run_configs["two"] = two_run_config
    config.data["two"] = two_data_config
    config.save()


def test_publish_overrides_data_for_all_run_configurations(
    copier_one_template_path: Path,
):
    template_path = copier_one_template_path
    config_path = GENERATED_FILES_DIR / "flexlate-dev.yaml"
    _create_config_with_default_and_two_run_configs()

    publish_all_templates(
        template_path,
        GENERATED_FILES_DIR,
        config_path=config_path,
        no_input=True,
        always_include_default=True,
        data=dict(q2=3),
    )

    folder_names = ["default", "out-one", "out-two"]
    for folder_name in folder_names:
        project_path = GENERATED_FILES_DIR / folder_name
        expect_file = project_path / "a1.txt"
        assert expect_file.read_text() == "3"
        # Check that post init but not post update was run
        assert (project_path / f"{folder_name}-one.txt").exists()
        assert not (project_path / f"{folder_name}-two.txt").exists()
