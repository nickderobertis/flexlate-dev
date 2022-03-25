import contextlib
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

from flexlate.main import Flexlate
import flexlate.exc as flexlate_exc
from git import Repo
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from flexlate.template_data import TemplateData
from flexlate.config import FlexlateConfig

from flexlate_dev.config import FlexlateDevConfig, load_config, ServeConfig
from flexlate_dev.gituitls import stage_and_commit_all
from flexlate_dev.styles import (
    print_styled,
    INFO_STYLE,
    SUCCESS_STYLE,
    ACTION_REQUIRED_STYLE,
)


def serve_template(
    template_path: Path = Path("."),
    out_path: Optional[Path] = None,
    no_input: bool = False,
    auto_commit: bool = True,
    config_path: Optional[Path] = None,
    save: bool = False,
):
    config = load_config(config_path)

    with run_server(
        config,
        template_path=template_path,
        out_path=out_path,
        no_input=no_input,
        auto_commit=auto_commit,
        save=save,
    ):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return


@contextlib.contextmanager
def run_server(
    config: FlexlateDevConfig,
    template_path: Path = Path("."),
    out_path: Optional[Path] = None,
    no_input: bool = False,
    auto_commit: bool = True,
    save: bool = False,
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
        no_input=no_input,
        auto_commit=auto_commit,
        save=save,
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


old = 0.0


class ServerEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        config: FlexlateDevConfig,
        template_path: Path,
        out_root: Path,
        no_input: bool = False,
        auto_commit: bool = True,
        save: bool = False,
    ):
        super().__init__()
        self.config = config
        self.template_path = template_path
        self.out_root = out_root
        self.no_input = no_input
        self.auto_commit = auto_commit
        self.save = save
        self.folder: Optional[str] = None
        self.repo: Optional[Repo] = None
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
        if self.repo is None:
            raise ValueError("repo must not be None")

        try:
            self.fxt.update(project_path=self.out_path, no_input=True)
        except flexlate_exc.TriedToCommitButNoChangesException:
            print_styled("Update did not have any changes", INFO_STYLE)
        except flexlate_exc.GitRepoDirtyException:
            if self.auto_commit:
                stage_and_commit_all(self.repo, "Auto-commit manual changes")
                print_styled(
                    "Detected manual changes to generated files and auto_commit=True, committing",
                    INFO_STYLE,
                )
                self.sync_output()
            else:
                print_styled(
                    "Detected manual changes to generated files and auto_commit=False. Please manually commit the changes to continue updating",
                    ACTION_REQUIRED_STYLE,
                )
        else:
            self._save_data_from_flexlate_if_necessary()

    def _initialize_project(self):
        self.folder = self.fxt.init_project_from(
            str(self.template_path),
            path=self.out_root,
            no_input=self.no_input,
            data=self.config.serve.data,
        )
        self._save_data_from_flexlate_if_necessary()
        self.repo = Repo(self.out_path)
        self.initialized = True

    def _save_data_from_flexlate_if_necessary(self):
        if not self.save:
            return
        data = _get_data_from_flexlate_config(self.out_path)
        self.config.serve.data = data
        self.config.save()


def _get_data_from_flexlate_config(folder: Path) -> TemplateData:
    config_path = folder / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    return at.data
