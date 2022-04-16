from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent

TESTS_DIR = Path(__file__).parent
INPUT_FILES_DIR = TESTS_DIR / "input_files"
GENERATED_FILES_DIR = TESTS_DIR / "generated"

TEMPLATES_DIR = INPUT_FILES_DIR / "templates"
INPUT_CONFIGS_DIR = INPUT_FILES_DIR / "configs"

COPIERS_DIR = TEMPLATES_DIR / "copiers"
COPIER_ONE_NAME = "one"
COPIER_ONE_DIR = COPIERS_DIR / COPIER_ONE_NAME

WITH_USER_COMMAND_CONFIG_PATH = INPUT_CONFIGS_DIR / "with_user_command.yaml"
BLOCKING_COMMAND_CONFIG_PATH = INPUT_CONFIGS_DIR / "blocking_command.yaml"
