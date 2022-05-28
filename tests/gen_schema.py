from pathlib import Path

from flexlate_dev.config_schema import create_config_schema
from tests.config import SCHEMA_PATH


def main(path: Path = SCHEMA_PATH):
    schema = create_config_schema()
    path.write_text(schema)


if __name__ == "__main__":
    main()
