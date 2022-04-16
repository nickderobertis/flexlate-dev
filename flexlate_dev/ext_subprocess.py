import subprocess
import sys
import threading

from flexlate_dev.styles import print_styled, INFO_STYLE


def run_command_stream_output(cmd: str):
    print_styled(f"Running command: {cmd}", INFO_STYLE)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    _stream_output_from_process(process)


def run_command_in_background_stream_output(cmd: str):
    print_styled(f"Running command: {cmd}", INFO_STYLE)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output_thread = threading.Thread(
        target=_stream_output_from_process, args=(process,), daemon=True
    )
    output_thread.start()


def _stream_output_from_process(process: subprocess.Popen):
    for line in iter(process.stdout.readline, b""):  # type: ignore
        sys.stdout.write(line.decode("utf-8"))
