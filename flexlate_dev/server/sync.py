import contextlib
import os
from pathlib import Path
from typing import Iterator, Optional

from flexlate import Flexlate
from flexlate.template_data import TemplateData
from git import Repo
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from flexlate_dev.config import DEFAULT_PROJECT_NAME, FlexlateDevConfig
from flexlate_dev.dict_merge import merge_dicts_preferring_non_none
from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.logger import log
from flexlate_dev.project_ops import update_or_initialize_project_get_folder
from flexlate_dev.styles import INFO_STYLE, print_styled

old = 0.0


class ServerEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        config: FlexlateDevConfig,
        template_path: Path,
        out_root: Path,
        run_config_name: Optional[str] = None,
        no_input: bool = False,
        auto_commit: bool = True,
        save: bool = False,
        data: Optional[TemplateData] = None,
        folder_name: Optional[str] = None,
    ):
        super().__init__()
        self.config = config
        self.run_config_name = run_config_name
        self.run_config = config.get_full_run_config(
            ExternalCLICommandType.SERVE, run_config_name
        )
        self.template_path = template_path
        self.out_root = out_root
        self.no_input = no_input
        self.auto_commit = auto_commit
        self.save = save
        self.cli_data = data
        self.cli_folder_name = folder_name
        self.folder: Optional[str] = None
        self.repo: Optional[Repo] = None
        self.fxt = Flexlate()

    @property
    def out_path(self) -> Path:
        if self.folder is None:
            raise ValueError("folder must be set")
        return self.out_root / self.folder

    @property
    def data(self) -> TemplateData:
        return merge_dicts_preferring_non_none(
            self.run_config.data.data if self.run_config.data else {},
            self.cli_data or {},
        )

    def on_modified(self, event: FileSystemEvent):
        global old
        super().on_modified(event)
        log.debug(f"on_modified called with {event=}")
        if not os.path.exists(event.src_path):
            log.debug(f"{event.src_path} does not exist, will not update")
            return

        relative_path = Path(event.src_path).relative_to(self.template_path)
        if relative_path == Path("."):
            # Watchdog seems to throw events on the whole directory after a file in the directory changed, ignore those
            log.debug("Got root template folder as change, ignoring")
            return
        if self.run_config.ignore_matches(relative_path):
            # Ignored file changed, don't trigger reload
            log.debug(f"Ignored file {relative_path} changed, ignoring")
            return

        # Watchdog has a bug where two events will be triggered very quickly for one modification.
        # Track whether it's been at least a half second since the last modification, and only then
        # consider it a valid event
        stat_buf = os.stat(event.src_path)
        new = stat_buf.st_mtime
        if (new - old) > 0.5:
            # This is a valid event, now the main logic
            print_styled(f"Detected change in {event.src_path}", INFO_STYLE)
            self.sync_output()
        else:
            log.debug(f"Ignoring duplicate event {event.src_path}")
        old = new

    def sync_output(self):
        self.folder = update_or_initialize_project_get_folder(
            self.template_path,
            self.out_root,
            self.config,
            self.run_config,
            data=self.data,
            no_input=self.no_input,
            auto_commit=self.auto_commit,
            save=self.save,
            known_folder_name=self.folder,
            default_folder_name=self.cli_folder_name
            or (
                self.run_config.data.use_folder_name
                if self.run_config.data
                else DEFAULT_PROJECT_NAME
            ),
        )
        self.repo = Repo(self.out_path)


class SyncServerManager:
    def __init__(self, handler: ServerEventHandler):
        self.observer = Observer()
        self.handler = handler

    def initial_start(self):
        self.handler.sync_output()  # do a sync before starting watcher
        self.start()

    def start(self):
        # setting up inotify and specifying path to watch
        self.observer.schedule(
            self.handler, str(self.handler.template_path), recursive=True
        )
        self.observer.start()
        log.debug("Watching for changes in template folder in sync server manager")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        log.debug(
            "Stopped watching for changes in template folder in sync server manager"
        )
        # Recycle observer so that it can be restarted
        self.observer = Observer()

    def __enter__(self) -> "SyncServerManager":
        self.initial_start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


@contextlib.contextmanager
def pause_sync(manager: SyncServerManager):
    manager.stop()
    yield
    manager.start()


@contextlib.contextmanager
def create_sync_server(
    config: FlexlateDevConfig,
    template_path: Path,
    out_root: Path,
    run_config_name: Optional[str] = None,
    no_input: bool = False,
    auto_commit: bool = True,
    save: bool = False,
    data: Optional[TemplateData] = None,
    folder_name: Optional[str] = None,
) -> Iterator[SyncServerManager]:
    event_handler = ServerEventHandler(
        config,
        template_path,
        out_root,
        run_config_name=run_config_name,
        no_input=no_input,
        auto_commit=auto_commit,
        save=save,
        data=data,
        folder_name=folder_name,
    )
    with SyncServerManager(event_handler) as manager:
        yield manager
