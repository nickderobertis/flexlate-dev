from flexlate_dev.config import (
    FlexlateDevConfig,
    create_default_run_configs,
    UserDataConfiguration,
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


def gen_config_with_extend_data():
    base_data_config = UserDataConfiguration(data=dict(q1="a1", q2=2), folder_name="a")
    extend_data_config = UserDataConfiguration(
        data=dict(q2=20, q3="a3"), extends="base"
    )
    run_config = UserRunConfiguration(
        data_name="my-extend",
    )
    run_configs = {"my-run-config": run_config, **create_default_run_configs()}
    data_configs = {"base": base_data_config, "my-extend": extend_data_config}
    config = FlexlateDevConfig(run_configs=run_configs, data=data_configs)
    config.settings.custom_config_folder = INPUT_CONFIGS_DIR
    config.settings.config_name = "extend_data"
    return config


def gen_config_with_extend_run_config():
    base_run_config = UserRunConfiguration(
        pre_update=["touch something.txt"], post_update=["touch something_else.txt"]
    )
    extend_run_config = UserRunConfiguration(
        pre_update=["touch overridden.txt"],
        auto_commit_message="something",
        extends="base",
    )
    run_configs = {
        "my-run-config": extend_run_config,
        "base": base_run_config,
        **create_default_run_configs(),
    }
    config = FlexlateDevConfig(run_configs=run_configs)
    config.settings.custom_config_folder = INPUT_CONFIGS_DIR
    config.settings.config_name = "extend_run"
    return config


def gen_config_with_extend_default_run_config():
    extend_run_config = UserRunConfiguration(
        pre_update=["touch overridden.txt"],
        auto_commit_message="something",
        extends="default",
    )
    default_serve_config = UserRunConfiguration(
        pre_update=["touch something.txt"], post_update=["touch something_else.txt"]
    )
    run_configs = {
        "my-run-config": extend_run_config,
        **create_default_run_configs(),
        # Override default publish config so it does operations we can verify
        "default_serve": default_serve_config,
    }
    config = FlexlateDevConfig(run_configs=run_configs)
    config.settings.custom_config_folder = INPUT_CONFIGS_DIR
    config.settings.config_name = "extend_default_run"
    return config


if __name__ == "__main__":
    gen_config_with_user_commands().save()
    gen_config_with_blocking_command().save()
    gen_config_with_extend_data().save()
    gen_config_with_extend_run_config().save()
    gen_config_with_extend_default_run_config().save()
