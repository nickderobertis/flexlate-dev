import pytest
from jinja2 import Environment

from flexlate_dev.render import create_jinja_environment


@pytest.fixture(scope="session")
def jinja_env() -> Environment:
    yield create_jinja_environment()
