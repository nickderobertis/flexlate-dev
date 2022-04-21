"""
Handles resolving commands referenced by id so that the command_runner module
can focus on only running a sequence of commands. Also has context of the
different configuration hooks so that the command_runner module can be
focused on just running commands.
"""
from enum import Enum
from pathlib import Path
from typing import Optional, List, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from flexlate_dev.config import FlexlateDevConfig

from pydantic import BaseModel

from flexlate_dev.command_runner import Runnable, run_command_or_command_strs
from flexlate_dev.dirutils import change_directory_to
from flexlate_dev.styles import print_styled, INFO_STYLE
from flexlate_dev.user_command import UserCommand


class RunnerHookType(str, Enum):
    POST_INIT = "post_init"
    PRE_UPDATE = "pre_update"
    POST_UPDATE = "post_update"


class UserRunConfiguration(BaseModel):
    post_init: Optional[List[Runnable]] = None
    pre_update: Optional[List[Runnable]] = None
    post_update: Optional[List[Runnable]] = None
    data_name: Optional[str] = None
    out_root: Optional[Path] = None
    auto_commit_message: Optional[str] = None

    @property
    def commit_message(self) -> str:
        return self.auto_commit_message or "chore: auto-commit manual changes"


def run_user_hook(
    hook_type: RunnerHookType,
    out_path: Path,
    user_run_config: UserRunConfiguration,
    config: "FlexlateDevConfig",
):
    """
    Runs a hook of the given type.
    """
    hook: Optional[List[Runnable]] = getattr(user_run_config, hook_type.value)
    if hook is not None:
        commands = _create_command_list_resolving_references(hook, config)
        print_styled(f"Running {hook_type.value} commands", INFO_STYLE)
        with change_directory_to(out_path):
            run_command_or_command_strs(commands)


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
