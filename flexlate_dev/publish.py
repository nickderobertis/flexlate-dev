from pathlib import Path
from typing import Optional

from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.config import FlexlateDevConfig, DEFAULT_PROJECT_NAME, load_config
from flexlate_dev.project_ops import update_or_initialize_project_get_folder


def publish_template(
    template_path: Path,
    out_root: Path,
    run_config_name: Optional[str] = None,
    config_path: Optional[Path] = None,
    no_input: bool = False,
    save: bool = False,
    abort_on_conflict: bool = False,
):
    config = load_config(config_path)
    run_config = config.get_full_run_config(
        ExternalCLICommandType.PUBLISH, run_config_name
    )

    update_or_initialize_project_get_folder(
        template_path,
        out_root,
        config,
        run_config,
        data=run_config.data.data if run_config.data else None,
        no_input=no_input,
        auto_commit=False,
        save=save,
        abort_on_conflict=abort_on_conflict,
        default_folder_name=run_config.data.use_folder_name
        if run_config.data
        else DEFAULT_PROJECT_NAME,
    )
