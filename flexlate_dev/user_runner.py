"""
Handles resolving commands referenced by id so that the command_runner module
can focus on only running a sequence of commands. Also has context of the
different configuration hooks so that the command_runner module can be
focused on just running commands.
"""
from enum import Enum
from pathlib import Path
from typing import Optional, List, TYPE_CHECKING, cast, Any, Dict

import jinja2

from flexlate_dev.dict_merge import merge_dicts_preferring_non_none
from flexlate_dev.external_command_type import ExternalCLICommandType

if TYPE_CHECKING:
    from flexlate_dev.config import FlexlateDevConfig, FullRunConfiguration

from pydantic import BaseModel

from flexlate_dev.command_runner import Runnable, run_command_or_command_strs
from flexlate_dev.dirutils import change_directory_to
from flexlate_dev.styles import print_styled, INFO_STYLE
from flexlate_dev.user_command import UserCommand


class RunnerHookType(str, Enum):
    PRE_CHECK = "pre_check"
    POST_INIT = "post_init"
    PRE_UPDATE = "pre_update"
    POST_UPDATE = "post_update"


class RunConfiguration(BaseModel):
    pre_check: Optional[List[Runnable]] = None
    post_init: Optional[List[Runnable]] = None
    pre_update: Optional[List[Runnable]] = None
    post_update: Optional[List[Runnable]] = None
    data_name: Optional[str] = None
    out_root: Optional[Path] = None
    auto_commit_message: Optional[str] = None

    @property
    def commit_message(self) -> str:
        return self.auto_commit_message or "chore: auto-commit manual changes"


class UserRunConfiguration(RunConfiguration):
    extends: Optional[str] = None


class UserRootRunConfiguration(UserRunConfiguration):
    publish: Optional[UserRunConfiguration] = None
    serve: Optional[UserRunConfiguration] = None

    def get_run_config(self, command: ExternalCLICommandType) -> UserRunConfiguration:
        # Extend base configuration with command-specific configuration if it exists
        base_config: UserRunConfiguration = self
        if command == ExternalCLICommandType.PUBLISH and self.publish:
            config = UserRunConfiguration(
                **merge_dicts_preferring_non_none(
                    base_config.dict(), self.publish.dict()
                )
            )
        elif command == ExternalCLICommandType.SERVE and self.serve:
            config = UserRunConfiguration(
                **merge_dicts_preferring_non_none(base_config.dict(), self.serve.dict())
            )
        else:
            config = base_config
        return config


def run_user_hook(
    hook_type: RunnerHookType,
    out_path: Path,
    run_config: "FullRunConfiguration",
    config: "FlexlateDevConfig",
    jinja_env: jinja2.Environment,
):
    """
    Runs a hook of the given type.
    """
    hook: Optional[List[Runnable]] = getattr(run_config.config, hook_type.value)
    if hook is not None:
        commands = _create_command_list_resolving_references(hook, config)
        rendered_commands = _render_commands(commands, run_config, jinja_env)
        print_styled(f"Running {hook_type.value} commands", INFO_STYLE)
        with change_directory_to(out_path):
            run_command_or_command_strs(rendered_commands)


def _create_command_list_resolving_references(
    command_list: List[Runnable], config: "FlexlateDevConfig"
) -> List[UserCommand]:
    """
    Resolves references in the given command list.
    """
    resolved_command_list: List[UserCommand] = []
    for command in command_list:
        if isinstance(command, str):
            add_command = UserCommand.from_string(command)
        else:
            if command.is_reference:
                id = cast(str, command.id)
                add_command = config.get_global_command_by_id(id)
            else:
                add_command = command
        resolved_command_list.append(add_command)
    return resolved_command_list


def _render_commands(
    commands: List[UserCommand],
    run_config: "FullRunConfiguration",
    jinja_env: jinja2.Environment,
) -> List[UserCommand]:
    """
    Renders the given commands using the given jinja environment, returning new commands.
    """
    return [_render_command(command, run_config, jinja_env) for command in commands]


def _render_command(
    command: UserCommand,
    run_config: "FullRunConfiguration",
    jinja_env: jinja2.Environment,
) -> UserCommand:
    """
    Renders the given command using the given jinja environment, returning a new command.
    """
    data = run_config.to_jinja_data()
    update_dict: Dict[str, Any] = {}
    for attr in ["run", "name"]:
        value = getattr(command, attr)
        if value is not None:
            update_dict[attr] = jinja_env.from_string(value).render(data)
    return command.copy(update=update_dict)
