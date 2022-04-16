from flexlate_dev.config import (
    FlexlateDevConfig,
    create_default_run_configs,
)
from flexlate_dev.user_runner import UserRunConfiguration
from flexlate_dev.user_command import UserCommand
from tests.config import INPUT_CONFIGS_DIR


def gen_config_with_user_commands():
    """
    Generate a configuration file with a user command.
    """
    referenced_command = UserCommand(run="touch referenced.txt", id="separate_command")
    referencing_command = UserCommand(id="separate_command")
    run_config_command = UserCommand(run="touch user_command.txt")
    run_config = UserRunConfiguration(
        post_init=[run_config_command, referencing_command],
        post_update=["touch string_command.txt"],
    )
    run_configs = {"my-run-config": run_config, **create_default_run_configs()}
    config = FlexlateDevConfig(run_configs=run_configs, commands=[referenced_command])
    config.settings.custom_config_folder = INPUT_CONFIGS_DIR
    config.settings.config_name = "with_user_command"
    return config


def gen_config_with_blocking_command():
    """
    Generate a configuration file with a user command.
    """
    blocking_command = UserCommand(run="sleep 10", background=True)
    run_config = UserRunConfiguration(
        post_init=[blocking_command],
    )
    run_configs = {"my-run-config": run_config, **create_default_run_configs()}
    config = FlexlateDevConfig(run_configs=run_configs)
    config.settings.custom_config_folder = INPUT_CONFIGS_DIR
    config.settings.config_name = "blocking_command"
    return config


if __name__ == "__main__":
    gen_config_with_user_commands().save()
    gen_config_with_blocking_command().save()
