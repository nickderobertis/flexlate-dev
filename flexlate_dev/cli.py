from pathlib import Path
from typing import Optional

import typer

from flexlate_dev.server import serve_template

cli = typer.Typer()

TEMPLATE_PATH_DOC = "Location of template, can be a local path or URL"
NO_INPUT_DOC = "Whether to proceed without any input from the user"
NO_AUTO_COMMIT_DOC = (
    "Whether to skip automatically committing manual changes in the generated project"
)
CONFIG_PATH_DOC = "The location of the flexlate-dev configuration file to use"
SAVE_DOC = "Whether to save the config file with any changes from the run such as answering project questions"

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


@cli.command(name="serve")
def serve(
    out_path: Optional[Path] = typer.Argument(
        None,
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
    template_path: Path = TEMPLATE_PATH_OPTION,
    config_path: Optional[Path] = CONFIG_PATH_OPTION,
    save: bool = SAVE_OPTION,
):
    """
    Sync rendered output of a template
    """
    raise NotImplementedError


if __name__ == "__main__":
    cli()
