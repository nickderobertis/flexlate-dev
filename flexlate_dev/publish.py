from pathlib import Path
from typing import Optional, List

from flexlate.template_data import TemplateData

from flexlate_dev.dict_merge import merge_dicts_preferring_non_none
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
    data: Optional[TemplateData] = None,
    folder_name: Optional[str] = None,
):
    config = load_config(config_path)
    run_config = config.get_full_run_config(
        ExternalCLICommandType.PUBLISH, run_config_name
    )

    use_data = merge_dicts_preferring_non_none(
        run_config.data.data if run_config.data else {}, data or {}
    )

    update_or_initialize_project_get_folder(
        template_path,
        out_root,
        config,
        run_config,
        data=use_data,
        no_input=no_input,
        auto_commit=False,
        save=save,
        abort_on_conflict=abort_on_conflict,
        default_folder_name=folder_name
        or (
            run_config.data.use_folder_name if run_config.data else DEFAULT_PROJECT_NAME
        ),
    )


def publish_all_templates(
    template_path: Path,
    out_root: Path,
    config_path: Optional[Path] = None,
    always_include_default: bool = False,
    exclude: Optional[List[str]] = None,
    no_input: bool = False,
    save: bool = False,
    abort_on_conflict: bool = False,
    data: Optional[TemplateData] = None,
    folder_name: Optional[str] = None,
):
    config = load_config(config_path)
    exclude = exclude or []
    run_config_names = [
        name
        for name in config.get_run_config_names(
            always_include_default=always_include_default
        )
        if name not in exclude
    ]
    for run_config_name in run_config_names:
        publish_template(
            template_path,
            out_root,
            run_config_name=run_config_name,
            config_path=config_path,
            no_input=no_input,
            save=save,
            abort_on_conflict=abort_on_conflict,
            data=data,
            folder_name=folder_name,
        )
