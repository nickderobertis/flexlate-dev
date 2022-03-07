from pathlib import Path
from typing import Optional

import typer

from flexlate_dev.server import serve_template

cli = typer.Typer()


@cli.command(name="serve")
def serve(
    out_path: Optional[Path] = typer.Argument(
        None,
        help="Optional location to serve built template to, defaults to a temporary directory",
    ),
    template_path: Path = typer.Argument(
        Path("."), help="Location of template to serve"
    ),
):
    """
    Run a development server with auto-reloading to see rendered output of a template
    """
    serve_template(template_path, out_path)


@cli.command(name="publish")
def publish(
    out_path: Path = typer.Argument(
        ...,
        help="Optional location to publish built template to, defaults to a temporary directory",
    ),
    template_path: Path = typer.Argument(
        Path("."), help="Location of template to publish"
    )
):
    """
    Sync rendered output of a template
    """
    raise NotImplementedError


if __name__ == "__main__":
    cli()
