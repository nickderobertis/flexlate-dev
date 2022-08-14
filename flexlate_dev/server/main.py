import contextlib
import tempfile
import time
from pathlib import Path
from typing import Iterator, Optional

from flexlate.template_data import TemplateData

from flexlate_dev.config import FlexlateDevConfig, load_config
from flexlate_dev.server.back_sync import BackSyncServer
from flexlate_dev.server.sync import SyncServerManager, create_sync_server
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


class ServerContext:
    def __init__(
        self,
        sync_manager: SyncServerManager,
        back_sync_manager: Optional[BackSyncServer] = None,
    ):
        self.sync_manager = sync_manager
        self.back_sync_manager = back_sync_manager

    @property
    def is_back_syncing(self) -> bool:
        if self.back_sync_manager is None:
            return False
        return self.back_sync_manager.is_syncing

    @property
    def back_sync_is_sleeping(self) -> bool:
        if self.back_sync_manager is None:
            return False
        return self.back_sync_manager.is_sleeping


@contextlib.contextmanager
def run_server(
    config: FlexlateDevConfig,
    run_config_name: Optional[str] = None,
    template_path: Path = Path("."),
    out_path: Optional[Path] = None,
    back_sync: bool = False,
    no_input: bool = False,
    auto_commit: bool = True,
    back_sync_auto_commit: bool = True,
    back_sync_check_interval_seconds: int = 1,
    save: bool = False,
    data: Optional[TemplateData] = None,
    folder_name: Optional[str] = None,
) -> Iterator[ServerContext]:
    temp_file: Optional[tempfile.TemporaryDirectory] = None
    if out_path is None:
        temp_file = tempfile.TemporaryDirectory()
        out_path = Path(temp_file.name)
    print_styled(
        f"Starting server, watching for changes in {template_path}. Generating output at {out_path}",
        INFO_STYLE,
    )
    with create_sync_server(
        config,
        template_path,
        out_path,
        run_config_name=run_config_name,
        no_input=no_input,
        auto_commit=auto_commit,
        save=save,
        data=data,
        folder_name=folder_name,
    ) as sync_manager:

        out_folder = sync_manager.handler.out_path

        print_styled(
            f"Running auto-reloader, updating {out_folder} with changes to {template_path}",
            SUCCESS_STYLE,
        )

        if back_sync:
            with BackSyncServer(
                template_path,
                out_folder,
                sync_manager,
                auto_commit=back_sync_auto_commit,
                check_interval_seconds=back_sync_check_interval_seconds,
            ) as back_sync_manager:
                yield ServerContext(sync_manager, back_sync_manager)
        else:
            yield ServerContext(sync_manager)

    if temp_file is not None:
        temp_file.cleanup()
