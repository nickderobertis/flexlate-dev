from flexlate_dev.config import SCHEMA_URL
from flexlate_dev.config_schema import create_config_schema
from tests.config import SCHEMA_PATH
from tests.gen_configs import gen_config_with_user_commands


def test_config_schema():
    schema_contents = SCHEMA_PATH.read_text()
    assert create_config_schema() == schema_contents


def test_schema_in_saved_config():
    config = gen_config_with_user_commands()
    config.save()
    config_contents = config.settings.config_location.read_text()
    assert SCHEMA_URL in config_contents
