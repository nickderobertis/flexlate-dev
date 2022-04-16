from flexlate_dev.command_runner import run_command_or_command_strs
from flexlate_dev.user_command import UserCommand
from tests.config import GENERATED_FILES_DIR

from tests.fixtures.temp_dir import inside_generated_dir


def test_run_str_command(inside_generated_dir):
    expect_path = GENERATED_FILES_DIR / "woo.txt"
    assert not expect_path.exists()
    run_command_or_command_strs(["touch woo.txt"])
    assert expect_path.exists()


def test_run_command(inside_generated_dir):
    expect_path = GENERATED_FILES_DIR / "woo.txt"
    command = UserCommand(run="touch woo.txt")
    assert not expect_path.exists()
    run_command_or_command_strs([command])
    assert expect_path.exists()
