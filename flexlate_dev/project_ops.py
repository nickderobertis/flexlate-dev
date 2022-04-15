from pathlib import Path
from typing import Optional

from flexlate import Flexlate
from flexlate.config import FlexlateConfig
from flexlate.template_data import TemplateData
from flexlate import exc as flexlate_exc
from git import Repo

from flexlate_dev.config import (
    FlexlateDevConfig,
    FullRunConfiguration,
    DEFAULT_PROJECT_NAME,
)
from flexlate_dev.dirutils import change_directory_to
from flexlate_dev.ext_subprocess import run_commands_stream_output
from flexlate_dev.gituitls import stage_and_commit_all
from flexlate_dev.styles import print_styled, INFO_STYLE, ACTION_REQUIRED_STYLE

fxt = Flexlate()


def update_or_initialize_project_get_folder(
    template_path: Path,
    out_root: Path,
    config: FlexlateDevConfig,
    run_config: FullRunConfiguration,
    no_input: bool = False,
    data: Optional[TemplateData] = None,
    save: bool = False,
    abort_on_conflict: bool = False,
    auto_commit: bool = True,
    known_folder_name: Optional[str] = None,
    default_folder_name: str = DEFAULT_PROJECT_NAME,
) -> str:
    def init_project() -> str:
        return initialize_project_get_folder(
            template_path,
            out_root,
            config,
            run_config,
            no_input=no_input,
            data=data,
            save=save,
            default_folder_name=default_folder_name,
        )

    folder = known_folder_name or (
        run_config.data.folder_name if run_config.data else None
    )
    if folder is None:
        print_styled(
            "No folder name in the config, defaulting to initializing the project",
            INFO_STYLE,
        )
        return init_project()

    out_path = out_root / folder
    if out_path.exists():
        print_styled(f"{out_path} exists, updating project", INFO_STYLE)
        update_project(
            out_path,
            config,
            run_config,
            data=data,
            no_input=no_input,
            abort_on_conflict=abort_on_conflict,
            auto_commit=auto_commit,
            save=save,
        )
        return folder

    print_styled(f"{out_path} does not exist, initializing project", INFO_STYLE)
    return init_project()


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
    auto_commit: bool = True,
    save: bool = True,
):
    if run_config.config.pre_update:
        print_styled("Running pre-update commands", INFO_STYLE)
        with change_directory_to(out_path):
            run_commands_stream_output(run_config.config.pre_update)
    try:
        fxt.update(
            data=[data] if data else None,
            no_input=no_input,
            abort_on_conflict=abort_on_conflict,
            project_path=out_path,
        )
    except flexlate_exc.GitRepoDirtyException:
        if auto_commit:
            repo = Repo(out_path)
            stage_and_commit_all(repo, "Auto-commit manual changes")
            print_styled(
                "Detected manual changes to generated files and auto_commit=True, committing",
                INFO_STYLE,
            )
            fxt.update(
                data=[data] if data else None,
                no_input=no_input,
                abort_on_conflict=abort_on_conflict,
                project_path=out_path,
            )
        else:
            print_styled(
                "Detected manual changes to generated files and auto_commit=False. Please manually commit the changes to continue updating",
                ACTION_REQUIRED_STYLE,
            )
            return
    except flexlate_exc.TriedToCommitButNoChangesException:
        print_styled("Update did not have any changes", INFO_STYLE)
        return

    if run_config.config.post_update:
        print_styled("Running post-update commands", INFO_STYLE)
        with change_directory_to(out_path):
            run_commands_stream_output(run_config.config.post_update)
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
