from flexlate_dev.config import (
    FlexlateDevConfig,
    UserRunConfiguration,
    create_default_run_configs,
)
from flexlate_dev.user_command import UserCommand
from tests.config import INPUT_CONFIGS_DIR


def gen_config_with_user_command():
    """
    Generate a configuration file with a user command.
    """
    command = UserCommand(run="touch user_command.txt")
    run_config = UserRunConfiguration(
        post_init=[command], post_update=["touch string_command.txt"]
    )
    run_configs = {"my-run-config": run_config, **create_default_run_configs()}
    config = FlexlateDevConfig(run_configs=run_configs)
    config.settings.custom_config_folder = INPUT_CONFIGS_DIR
    config.settings.config_name = "with_user_command"
    return config


if __name__ == "__main__":
    config = gen_config_with_user_command()
    config.save()
