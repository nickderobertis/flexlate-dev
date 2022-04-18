from pathlib import Path
from typing import Optional

import typer

from flexlate_dev import get_version
from flexlate_dev.publish import publish_template
from flexlate_dev.server import serve_template
from flexlate_dev.styles import print_styled, INFO_STYLE

cli = typer.Typer()

TEMPLATE_PATH_DOC = "Location of template, can be a local path or URL"
NO_INPUT_DOC = "Whether to proceed without any input from the user"
NO_AUTO_COMMIT_DOC = (
    "Whether to skip automatically committing manual changes in the generated project"
)
CONFIG_PATH_DOC = "The location of the flexlate-dev configuration file to use"
SAVE_DOC = "Whether to save the config file with any changes from the run such as answering project questions"
RUN_CONFIG_NAME_DOC = "The name of the run configuration to use"

TEMPLATE_PATH_OPTION = typer.Option(
    Path("."),
    "--template",
    "-t",
    help=TEMPLATE_PATH_DOC,
)
NO_INPUT_OPTION = typer.Option(False, "--no-input", "-n", show_default=False)
NO_AUTO_COMMIT_OPTION = typer.Option(
    False, "--no-auto-commit", "-a", show_default=False
)
CONFIG_PATH_OPTION = typer.Option(None, "--config", "-c", show_default=False)
SAVE_OPTION = typer.Option(False, "--save", "-s", show_default=False)
RUN_CONFIG_ARGUMENT = typer.Argument(None, help=RUN_CONFIG_NAME_DOC)


@cli.callback(invoke_without_command=True)
def pre_execute(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        show_default=False,
        help="Show flexlate-dev and flexlate version, then exit",
    )
):
    # Support printing version and then existing with dfxt --version
    if version:
        version_number = get_version.get_flexlate_dev_version()
        flexlate_version = get_version.get_flexlate_version()
        message = "\n".join(
            [
                f"flexlate-dev: {version_number}",
                f"flexlate: {flexlate_version}",
            ]
        )
        print_styled(message, INFO_STYLE)
        exit(0)


@cli.command(name="serve")
def serve(
    run_config: Optional[str] = RUN_CONFIG_ARGUMENT,
    out_path: Optional[Path] = typer.Option(
        None,
        "--out",
        "-o",
        help="Optional location to serve built template to, defaults to a temporary directory",
    ),
    template_path: Path = TEMPLATE_PATH_OPTION,
    no_input: bool = NO_INPUT_OPTION,
    no_auto_commit: bool = NO_AUTO_COMMIT_OPTION,
    config_path: Optional[Path] = CONFIG_PATH_OPTION,
    save: bool = SAVE_OPTION,
):
    """
    Run a development server with auto-reloading to see rendered output of a template
    """
    serve_template(
        run_config,
        template_path,
        out_path,
        no_input=no_input,
        auto_commit=not no_auto_commit,
        config_path=config_path,
        save=save,
    )


@cli.command(name="publish")
def publish(
    out_path: Path = typer.Argument(
        ...,
        help="Location to publish built template to",
    ),
    run_config: Optional[str] = RUN_CONFIG_ARGUMENT,
    template_path: Path = TEMPLATE_PATH_OPTION,
    config_path: Optional[Path] = CONFIG_PATH_OPTION,
    no_input: bool = NO_INPUT_OPTION,
    save: bool = SAVE_OPTION,
):
    """
    Sync rendered output of a template
    """
    publish_template(
        template_path,
        out_path,
        run_config_name=run_config,
        config_path=config_path,
        save=save,
        no_input=no_input,
    )


if __name__ == "__main__":
    cli()
