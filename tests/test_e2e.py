from pathlib import Path

from flexlate_dev.server import serve_template
from tests.config import GENERATED_FILES_DIR
from tests.fixtures.template_path import copier_one_template_path


def test_server_creates_and_updates_template_on_change(copier_one_template_path: Path):
    template_path = copier_one_template_path
    serve_template(template_path, GENERATED_FILES_DIR, no_input=True)
