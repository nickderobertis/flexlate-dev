import time
import timeit
from contextlib import contextmanager
from pathlib import Path
from typing import Final, Callable

DEFAULT_TIMEOUT: Final = 5


def wait_until_path_exists(path: Path, timeout: int = DEFAULT_TIMEOUT):
    _wait_until_returns_true(
        path.exists, f"Could not find path {path}", timeout=timeout
    )


def wait_until_file_updates(
    path: Path, modified_time: float, timeout: int = DEFAULT_TIMEOUT
):
    def path_has_been_modified() -> bool:
        new_modified_time = path.lstat().st_mtime
        return new_modified_time > modified_time

    _wait_until_returns_true(
        path_has_been_modified,
        f"{path} was not updated. Content: {path.read_text()}",
        timeout=timeout,
    )


def wait_until_file_has_content(
    path: Path, modified_time: float, content: str, timeout: int = DEFAULT_TIMEOUT
):
    def file_has_new_content() -> bool:
        if not path.exists():
            return False
        new_modified_time = path.lstat().st_mtime
        if new_modified_time == modified_time:
            # File has not been modified, no need to read it
            return False
        file_content = path.read_text()
        return file_content == content

    _wait_until_returns_true(
        file_has_new_content,
        f"{path} never got the expected contents. Content: {path.read_text()}. Expect content: {content}",
        timeout=timeout,
    )


def _wait_until_returns_true(
    exit_callback: Callable[[], bool],
    error_message: str,
    timeout: int = DEFAULT_TIMEOUT,
):
    start_time = timeit.default_timer()
    while timeit.default_timer() - start_time < timeout:
        should_exit = exit_callback()
        if should_exit:
            return
        time.sleep(0.1)
    # Timed out
    raise TestTimeoutException(f"{error_message} after {timeout}s")


class TestTimeoutException(Exception):
    pass
