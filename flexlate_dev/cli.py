from pathlib import Path
from typing import Optional

import typer

from flexlate_dev.server import serve_template

cli = typer.Typer()


@cli.command(name="serve")
def serve(
    template_path: Path = typer.Argument(
        Path("."), help="Location of template to serve"
    ),
    out_path: Optional[Path] = typer.Argument(
        None,
        help="Optional location to serve built template to, defaults to a temporary directory",
    ),
):
    serve_template(template_path, out_path)


if __name__ == "__main__":
    cli()
