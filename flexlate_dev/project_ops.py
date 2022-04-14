from pathlib import Path
from typing import Optional

from flexlate import Flexlate
from flexlate.config import FlexlateConfig
from flexlate.template_data import TemplateData

from flexlate_dev.config import (
    FlexlateDevConfig,
    FullRunConfiguration,
    DEFAULT_PROJECT_NAME,
)

fxt = Flexlate()


def initialize_project_get_folder(
    template_path: Path,
    out_root: Path,
    config: FlexlateDevConfig,
    run_config: FullRunConfiguration,
    no_input: bool = False,
    data: Optional[TemplateData] = None,
    save: bool = True,
    default_folder_name: str = DEFAULT_PROJECT_NAME,
) -> str:
    folder = fxt.init_project_from(
        str(template_path),
        path=out_root,
        no_input=no_input,
        data=data,
        default_folder_name=default_folder_name,
    )
    if save:
        out_path = out_root / folder
        save_config(out_path, config, run_config)
    return folder


def save_config(
    out_path: Path, config: FlexlateDevConfig, run_config: FullRunConfiguration
):
    data = _get_data_from_flexlate_config(out_path)
    config.save_data_for_run_config(run_config, data)


def _get_data_from_flexlate_config(folder: Path) -> TemplateData:
    config_path = folder / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    return at.data
