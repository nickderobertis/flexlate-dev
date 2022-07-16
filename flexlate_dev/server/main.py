import contextlib
import tempfile
import time
from pathlib import Path
from typing import Optional

from flexlate.template_data import TemplateData
from watchdog.observers import Observer

from flexlate_dev.config import FlexlateDevConfig, load_config
from flexlate_dev.server.sync import ServerEventHandler
from flexlate_dev.styles import INFO_STYLE, SUCCESS_STYLE, print_styled


def serve_template(
    run_config_name: Optional[str] = None,
    template_path: Path = Path("."),
    out_path: Optional[Path] = None,
    back_sync: bool = False,
    no_input: bool = False,
    auto_commit: bool = True,
    config_path: Optional[Path] = None,
    save: bool = False,
    data: Optional[TemplateData] = None,
    folder_name: Optional[str] = None,
):
    config = load_config(config_path)

    with run_server(
        config,
        run_config_name=run_config_name,
        template_path=template_path,
        out_path=out_path,
        back_sync=back_sync,
        no_input=no_input,
        auto_commit=auto_commit,
        save=save,
        data=data,
        folder_name=folder_name,
    ):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return


@contextlib.contextmanager
def run_server(
    config: FlexlateDevConfig,
    run_config_name: Optional[str] = None,
    template_path: Path = Path("."),
    out_path: Optional[Path] = None,
    back_sync: bool = False,
    no_input: bool = False,
    auto_commit: bool = True,
    save: bool = False,
    data: Optional[TemplateData] = None,
    folder_name: Optional[str] = None,
):
    temp_file: Optional[tempfile.TemporaryDirectory] = None
    if out_path is None:
        temp_file = tempfile.TemporaryDirectory()
        out_path = Path(temp_file.name)
    # setting up inotify and specifying path to watch
    print_styled(
        f"Starting server, watching for changes in {template_path}. Generating output at {out_path}",
        INFO_STYLE,
    )
    observer = Observer()
    event_handler = ServerEventHandler(
        config,
        template_path,
        out_path,
        run_config_name=run_config_name,
        no_input=no_input,
        auto_commit=auto_commit,
        save=save,
        data=data,
        folder_name=folder_name,
    )
    event_handler.sync_output()  # do a sync before starting watcher
    observer.schedule(event_handler, str(template_path), recursive=True)
    observer.start()
    print_styled(
        f"Running auto-reloader, updating {event_handler.out_path} with changes to {template_path}",
        SUCCESS_STYLE,
    )

    yield

    observer.stop()
    observer.join()
    if temp_file is not None:
        temp_file.cleanup()
