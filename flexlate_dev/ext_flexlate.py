from pathlib import Path

from flexlate.config_manager import ConfigManager


def get_render_relative_root_in_template_from_project_path(project_path: Path) -> Path:
    config_manager = ConfigManager()
    config = config_manager.load_config(project_path)
    if len(config.template_sources) != 1:
        raise ValueError(
            "Must have only a single template source to extract relative root"
        )
    ts = config.template_sources[0]
    return ts.render_relative_root_in_template
