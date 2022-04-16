from typing import Sequence, Union

from flexlate_dev.ext_subprocess import run_command_stream_output
from flexlate_dev.user_command import UserCommand


def run_command_or_command_strs(cmds: Sequence[Union[str, UserCommand]]):
    for cmd in cmds:
        if isinstance(cmd, str):
            command = UserCommand.from_string(cmd)
        else:
            command = cmd
        run_command(command)


def run_command(cmd: UserCommand):
    run_command_stream_output(cmd.run)
