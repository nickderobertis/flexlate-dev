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
from flexlate_dev.dirutils import change_directory_to
from flexlate_dev.ext_subprocess import run_commands_stream_output
from flexlate_dev.styles import print_styled, INFO_STYLE

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
    out_path = out_root / folder
    if run_config.config.post_init:
        print_styled("Running post-init commands", INFO_STYLE)
        with change_directory_to(out_path):
            run_commands_stream_output(run_config.config.post_init)
    if save:
        _save_config(out_path, config, run_config)
    return folder


def update_project(
    out_path: Path,
    config: FlexlateDevConfig,
    run_config: FullRunConfiguration,
    data: Optional[TemplateData] = None,
    no_input: bool = False,
    abort_on_conflict: bool = False,
    save: bool = True,
):
    fxt.update(
        data=[data] if data else None,
        no_input=no_input,
        abort_on_conflict=abort_on_conflict,
        project_path=out_path,
    )
    if save:
        _save_config(out_path, config, run_config)


def _save_config(
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
