import contextlib
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

from flexlate.main import Flexlate
import flexlate.exc as flexlate_exc
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from flexlate_dev.styles import print_styled, INFO_STYLE, SUCCESS_STYLE


def serve_template(
    template_path: Path = Path("."),
    out_path: Optional[Path] = None,
    no_input: bool = False,
):
    with run_server(template_path=template_path, out_path=out_path, no_input=no_input):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return


@contextlib.contextmanager
def run_server(
    template_path: Path = Path("."),
    out_path: Optional[Path] = None,
    no_input: bool = False,
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
    event_handler = ServerEventHandler(template_path, out_path, no_input=no_input)
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


old = 0.0


class ServerEventHandler(FileSystemEventHandler):
    def __init__(self, template_path: Path, out_root: Path, no_input: bool = False):
        super().__init__()
        self.template_path = template_path
        self.out_root = out_root
        self.no_input = no_input
        self.folder: Optional[str] = None
        self.initialized = False
        self.fxt = Flexlate()

    @property
    def out_path(self) -> Path:
        if self.folder is None:
            raise ValueError("folder must be set")
        return self.out_root / self.folder

    def on_modified(self, event: FileSystemEvent):
        global old
        super().on_modified(event)
        if not os.path.exists(event.src_path):
            return
        # Watchdog has a bug where two events will be triggered very quickly for one modification.
        # Track whether it's been at least a half second since the last modification, and only then
        # consider it a valid event
        stat_buf = os.stat(event.src_path)
        new = stat_buf.st_mtime
        if (new - old) > 0.5:
            # This is a valid event, now the main logic
            self.sync_output()
        old = new

    def sync_output(self):
        """
        Run build using subprocess so that imports will be executed every time
        :param file_path:
        :return:
        """
        if not self.initialized:
            return self._initialize_project()

        try:
            self.fxt.update(project_path=self.out_path, no_input=True)
        except flexlate_exc.TriedToCommitButNoChangesException:
            print_styled("Update did not have any changes", INFO_STYLE)

    def _initialize_project(self):
        self.folder = self.fxt.init_project_from(
            str(self.template_path), path=self.out_root, no_input=self.no_input
        )
        self.initialized = True
