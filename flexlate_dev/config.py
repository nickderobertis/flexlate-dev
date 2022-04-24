from pathlib import Path
from typing import Optional, Dict, List, Final, Any

from flexlate.template_data import TemplateData
from pyappconf import BaseConfig, AppConfig, ConfigFormats
from pydantic import BaseModel, Field

from flexlate_dev.dict_merge import merge_dicts_preferring_non_none
from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.exc import (
    NoSuchRunConfigurationException,
    NoSuchDataException,
    NoSuchCommandException,
)
from flexlate_dev.user_command import UserCommand
from flexlate_dev.user_runner import (
    UserRootRunConfiguration,
    RunConfiguration,
    UserRunConfiguration,
)

DEFAULT_PROJECT_NAME: Final[str] = "project"


class DataConfiguration(BaseModel):
    data: TemplateData = Field(default_factory=dict)
    folder_name: Optional[str] = None

    @property
    def use_folder_name(self) -> str:
        return self.folder_name or DEFAULT_PROJECT_NAME


class UserDataConfiguration(DataConfiguration):
    extends: Optional[str] = None


class FullRunConfiguration(BaseModel):
    config: RunConfiguration
    data: Optional[DataConfiguration]

    def to_jinja_data(self) -> Dict[str, Any]:
        return self.dict()


def create_default_run_configs() -> Dict[str, UserRootRunConfiguration]:
    default_publish = UserRootRunConfiguration(
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
    data: Dict[str, UserDataConfiguration] = Field(default_factory=dict)
    commands: List[UserCommand] = Field(default_factory=list)
    run_configs: Dict[str, UserRootRunConfiguration] = Field(
        default_factory=create_default_run_configs
    )
    _settings = AppConfig(
        app_name="flexlate-dev",
        default_format=ConfigFormats.YAML,
        config_name="flexlate-dev",
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
        return DataConfiguration(data=extended_data, folder_name=folder_name)

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
