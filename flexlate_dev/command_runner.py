from typing import Sequence, Union

from flexlate_dev.ext_subprocess import (
    run_command_in_background_stream_output,
    run_command_stream_output,
)
from flexlate_dev.styles import INFO_STYLE, print_styled
from flexlate_dev.user_command import UserCommand

Runnable = Union[UserCommand, str]


def run_command_or_command_strs(cmds: Sequence[Runnable]):
    for cmd in cmds:
        if isinstance(cmd, str):
            command = UserCommand.from_string(cmd)
        else:
            command = cmd
        run_command(command)


def run_command(cmd: UserCommand):
    print_styled(f"Running command: {cmd.display_name}", INFO_STYLE)
    if cmd.run is None:
        raise ValueError(f"Cannot run command {cmd} as run=None")
    if cmd.background:
        run_command_in_background_stream_output(cmd.run)
    else:
        run_command_stream_output(cmd.run)
