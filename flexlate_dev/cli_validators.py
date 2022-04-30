import ast

from flexlate.template_data import TemplateData


def parse_data_from_str(data_str: str) -> TemplateData:
    error = ValueError('--data must be a dictionary, e.g. --data \'{"foo": "bar"}\'')
    try:
        parsed = ast.literal_eval(data_str)
    except ValueError:
        raise error
    if not isinstance(parsed, dict):
        raise error
    return parsed
