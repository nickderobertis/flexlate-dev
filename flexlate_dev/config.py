from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Union

from flexlate.template_data import TemplateData
from pyappconf import AppConfig, BaseConfig, ConfigFormats
from pydantic import BaseModel, Field

from flexlate_dev.dict_merge import merge_dicts_preferring_non_none
from flexlate_dev.exc import (
    NoSuchCommandException,
    NoSuchDataException,
    NoSuchRunConfigurationException,
)
from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.ignore import IgnoreSpecification
from flexlate_dev.user_command import UserCommand
from flexlate_dev.user_runner import (
    RunConfiguration,
    UserRootRunConfiguration,
    UserRunConfiguration,
)

DEFAULT_PROJECT_NAME: Final[str] = "project"
SCHEMA_URL: Final[
    str
] = "https://nickderobertis.github.io/flexlate-dev/_static/config-schema.json"


class DataConfiguration(BaseModel):
    data: TemplateData = Field(
        default_factory=dict,
        description="Key-value pairs of data to be used in the template",
    )
    folder_name: Optional[str] = Field(
        default=None,
        description="Name of the folder to be created for the project, "
        "if it is a template type that does not specify a name",
    )
    ignore: List[str] = Field(
        default_factory=list,
        description="List of files or folders to ignore when creating the project. "
        "Full git wildmatch syntax (like .gitignore) is supported including negations",
    )

    @property
    def use_folder_name(self) -> str:
        return self.folder_name or DEFAULT_PROJECT_NAME


class UserDataConfiguration(DataConfiguration):
    extends: Optional[str] = Field(
        default=None, description="Name of the data configuration to extend"
    )


@dataclass
class FullRunConfiguration:
    config: RunConfiguration
    data: Optional[DataConfiguration]
    _ignore_spec: IgnoreSpecification = field(init=False)

    def __post_init__(self):
        self._ignore_spec = IgnoreSpecification(ignore_list=self._use_ignore)

    def to_jinja_data(self) -> Dict[str, Any]:
        return dict(
            config=self.config.dict(), data=self.data.dict() if self.data else {}
        )

    @property
    def _use_ignore(self) -> List[str]:
        return self.data.ignore if self.data is not None else []

    def ignore_matches(self, to_match: Union[str, Path]) -> bool:
        return self._ignore_spec.file_is_ignored(to_match)


def create_default_run_configs() -> Dict[str, UserRootRunConfiguration]:
    default_publish = UserRootRunConfiguration(
        pre_check=[
            'if [ -n "$(find . -prune -empty 2>/dev/null)" ]; '
            "then gh repo clone {{ data.folder_name }} .; "
            "else git pull origin master; "
            "fi"
        ],
        post_init=[
            "gh repo create --public --source=.",
            "git push origin master",
            "git push --all origin",
        ],
        post_update=["fxt merge", "git push --all origin"],
    )
    return dict(
        default=UserRootRunConfiguration(publish=default_publish),
    )


class FlexlateDevConfig(BaseConfig):
    """
    Flexlate Dev configuration.
    """

    data: Dict[str, UserDataConfiguration] = Field(
        default_factory=dict, description="Data configurations by name"
    )
    commands: List[UserCommand] = Field(
        default_factory=list,
        description="Commands that can be used across multiple configurations",
    )
    run_configs: Dict[str, UserRootRunConfiguration] = Field(
        default_factory=create_default_run_configs,
        description="Root run configurations by name",
    )
    _settings = AppConfig(
        app_name="flexlate-dev",
        default_format=ConfigFormats.YAML,
        config_name="flexlate-dev",
        schema_url=SCHEMA_URL,
    )

    def save(self, serializer_kwargs: Optional[Dict[str, Any]] = None, **kwargs):
        all_kwargs = dict(exclude_none=True, **kwargs)
        return super().save(serializer_kwargs=serializer_kwargs, **all_kwargs)

    def get_full_run_config(
        self, command: ExternalCLICommandType, name: Optional[str] = None
    ) -> FullRunConfiguration:
        user_run_config = self.get_run_config(command, name)
        if user_run_config.data_name is None:
            data_config = self.get_default_data()
        else:
            data_config = self.get_data_config(user_run_config.data_name)
        return FullRunConfiguration(config=user_run_config, data=data_config)

    def get_run_config(
        self, command: ExternalCLICommandType, name: Optional[str] = None
    ) -> UserRunConfiguration:
        name = name or "default"
        user_root_run_config = self.run_configs.get(name)
        if not user_root_run_config:
            raise NoSuchRunConfigurationException(name)
        user_run_config = user_root_run_config.get_run_config(command)
        if not user_run_config.extends:
            # No extends, so return the config as-is
            return user_run_config
        # Create a new config by extending the referenced config
        extends_config = self.get_run_config(command, user_run_config.extends)
        return UserRunConfiguration(
            **merge_dicts_preferring_non_none(
                extends_config.dict(), user_run_config.dict()
            )
        )

    def get_run_config_names(self, always_include_default: bool = False) -> List[str]:
        names = list(self.run_configs.keys())
        if not always_include_default and len(names) > 1:
            names.remove("default")
        return names

    def get_default_data(self) -> Optional[DataConfiguration]:
        try:
            return self.get_data_config("default")
        except NoSuchDataException:
            return None

    def get_data_config(self, name: str) -> DataConfiguration:
        user_data_config = self.data.get(name)
        if not user_data_config:
            raise NoSuchDataException(name)
        if not user_data_config.extends:
            # No extends, so return the config as-is
            return user_data_config
        # Create a new config by extending the referenced config
        extends_config = self.get_data_config(user_data_config.extends)
        extended_data = {**extends_config.data, **user_data_config.data}
        folder_name = user_data_config.folder_name or extends_config.folder_name
        if extends_config.ignore is None:
            extended_ignore = user_data_config.ignore
        elif user_data_config.ignore is None:
            extended_ignore = extends_config.ignore
        else:
            # Both specified ignores, extend the list
            extended_ignore = [*extends_config.ignore, *user_data_config.ignore]
        return DataConfiguration(
            data=extended_data, folder_name=folder_name, ignore=extended_ignore
        )

    def save_data_for_run_config(
        self, run_config: FullRunConfiguration, data: TemplateData
    ):
        data_name = run_config.config.data_name or "default"
        data_config = self.data.get(data_name) or UserDataConfiguration()
        new_data_config = data_config.copy(update=dict(data=data))
        run_config.config.data_name = data_name  # set to default if was previously None
        self.data[data_name] = new_data_config
        self.save()

    def get_global_command_by_id(self, id: str) -> UserCommand:
        for command in self.commands:
            if command.id == id:
                return command
        raise NoSuchCommandException(id)


def load_config(config_path: Optional[Path]) -> FlexlateDevConfig:
    if config_path is None:
        for possible_name in ["flexlate-dev.yaml", "flexlate-dev.yml"]:
            path = Path(possible_name)
            if path.exists():
                return FlexlateDevConfig.load(path)
    elif config_path.exists():
        return FlexlateDevConfig.load(config_path)
    else:
        # Passed config path, but does not exist, might be trying to save new config
        return FlexlateDevConfig.load_or_create(config_path.resolve())

    # Could not find any config, create a blank one at the default location
    return FlexlateDevConfig.load_or_create(Path("flexlate-dev.yaml").resolve())
