from pathlib import Path
from typing import Optional, Dict, List, Final, Any

from flexlate.template_data import TemplateData
from pyappconf import BaseConfig, AppConfig, ConfigFormats
from pydantic import BaseModel, Field

from flexlate_dev.external_command_type import ExternalCLICommandType
from flexlate_dev.exc import (
    NoSuchRunConfigurationException,
    NoSuchDataException,
    NoSuchCommandException,
)
from flexlate_dev.user_command import UserCommand
from flexlate_dev.user_runner import UserRunConfiguration

DEFAULT_PROJECT_NAME: Final[str] = "project"


class DataConfiguration(BaseModel):
    data: TemplateData = Field(default_factory=dict)
    folder_name: str = DEFAULT_PROJECT_NAME


class FullRunConfiguration(BaseModel):
    config: UserRunConfiguration
    data: Optional[DataConfiguration]


def create_default_run_configs() -> Dict[str, UserRunConfiguration]:
    return dict(
        default_serve=UserRunConfiguration(),
        default_publish=UserRunConfiguration(
            post_init=["gh repo create --source=."],
            post_update=["git push --all origin"],
        ),
    )


class FlexlateDevConfig(BaseConfig):
    data: Dict[str, DataConfiguration] = Field(default_factory=dict)
    commands: List[UserCommand] = Field(default_factory=list)
    run_configs: Dict[str, UserRunConfiguration] = Field(
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

    def get_run_config(
        self, command: ExternalCLICommandType, name: Optional[str] = None
    ) -> FullRunConfiguration:
        name = name or f"default_{command.value.casefold()}"
        user_run_config = self.run_configs.get(name)
        if not user_run_config:
            raise NoSuchRunConfigurationException(name)
        if user_run_config.data_name is None:
            data_config = self.data.get("default")
        else:
            data_config = self.data.get(user_run_config.data_name)
            if not data_config:
                raise NoSuchDataException(user_run_config.data_name)
        return FullRunConfiguration(config=user_run_config, data=data_config)

    def save_data_for_run_config(
        self, run_config: FullRunConfiguration, data: TemplateData
    ):
        data_name = run_config.config.data_name or "default"
        data_config = self.data.get(data_name) or DataConfiguration()
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
