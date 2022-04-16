from flexlate_dev.config import FlexlateDevConfig
from flexlate_dev.user_command import UserCommand
from tests.config import INPUT_CONFIGS_DIR, GENERATED_FILES_DIR
from tests.gen_configs import gen_config_with_user_commands

WITH_USER_COMMAND_PATH = INPUT_CONFIGS_DIR / "with_user_command.yaml"


def test_read_config_with_commands():
    with_user_command_config = FlexlateDevConfig.load(WITH_USER_COMMAND_PATH)
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
        WITH_USER_COMMAND_PATH.read_text()
        == (GENERATED_FILES_DIR / "with_user_command.yaml").read_text()
    )
