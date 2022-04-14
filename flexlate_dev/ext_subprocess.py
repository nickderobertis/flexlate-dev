import subprocess
import shlex
import sys
from typing import Sequence

from flexlate_dev.styles import print_styled, INFO_STYLE


def run_command_stream_output(cmd: str):
    print_styled(f"Running command: {cmd}", INFO_STYLE)
    split_command = shlex.split(cmd)
    process = subprocess.Popen(split_command, stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, b""):
        sys.stdout.write(line.decode("utf-8"))


def run_commands_stream_output(cmds: Sequence[str]):
    for cmd in cmds:
        run_command_stream_output(cmd)
