from jinja2 import Environment


def create_jinja_environment(**options) -> Environment:
    """
    Creates a jinja environment for rendering templates.
    :return: jinja2 environment
    """
    env = Environment(
        **options,
    )
    return env
