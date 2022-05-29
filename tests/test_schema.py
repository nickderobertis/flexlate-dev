from flexlate_dev.config_schema import create_config_schema
from tests.config import SCHEMA_PATH


def test_config_schema():
    schema_contents = SCHEMA_PATH.read_text()
    assert create_config_schema() == schema_contents
