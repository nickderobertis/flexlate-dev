from flexlate_dev.config import FlexlateDevConfig
from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.user_command import UserCommand
from tests.config import (
    INPUT_CONFIGS_DIR,
    GENERATED_FILES_DIR,
    WITH_USER_COMMAND_CONFIG_PATH,
    EXTEND_DATA_CONFIG_PATH,
    EXTEND_RUN_CONFIG_PATH,
    EXTEND_DEFAULT_RUN_CONFIG_PATH,
)
from tests.gen_configs import gen_config_with_user_commands


def test_read_config_with_commands():
    with_user_command_config = FlexlateDevConfig.load(WITH_USER_COMMAND_CONFIG_PATH)
    run_config = with_user_command_config.run_configs["my-run-config"]
    assert run_config.post_update == ["touch string_command.txt"]
    assert len(run_config.post_init) == 2
    post_init_inline_command = run_config.post_init[0]
    assert isinstance(post_init_inline_command, UserCommand)
    assert post_init_inline_command.run == "touch user_command.txt"

    post_init_referenced_command = run_config.post_init[1]
    assert isinstance(post_init_referenced_command, UserCommand)
    assert post_init_referenced_command.id == "separate_command"


def test_write_config_with_commands():
    config = gen_config_with_user_commands()
    config.settings.custom_config_folder = GENERATED_FILES_DIR
    config.save()
    assert (
        WITH_USER_COMMAND_CONFIG_PATH.read_text()
        == (GENERATED_FILES_DIR / "with_user_command.yaml").read_text()
    )


def test_read_extended_data():
    config = FlexlateDevConfig.load(EXTEND_DATA_CONFIG_PATH)
    data_config = config.get_data_config("my-extend")
    assert data_config.data == dict(q1="a1", q2=20, q3="a3")
    assert data_config.folder_name == "a"


def test_read_extended_run_config():
    config = FlexlateDevConfig.load(EXTEND_RUN_CONFIG_PATH)
    run_config = config.get_full_run_config(
        ExternalCLICommandType.SERVE, "my-run-config"
    )
    assert run_config.config.pre_update == ["touch overridden.txt"]
    assert run_config.config.post_update == ["touch something_else.txt"]
    assert run_config.config.auto_commit_message == "something"


def test_read_extended_default_run_config():
    config = FlexlateDevConfig.load(EXTEND_DEFAULT_RUN_CONFIG_PATH)
    run_config = config.get_full_run_config(
        ExternalCLICommandType.SERVE, "my-run-config"
    )
    assert run_config.config.pre_update == ["touch overridden.txt"]
    assert run_config.config.post_update == ["touch something_else.txt"]
    assert run_config.config.auto_commit_message == "something"
