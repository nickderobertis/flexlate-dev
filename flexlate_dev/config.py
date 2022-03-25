from pathlib import Path
from typing import Optional

from flexlate.template_data import TemplateData
from pyappconf import BaseConfig, AppConfig, ConfigFormats
from pydantic import BaseModel, Field


class ServeConfig(BaseModel):
    data: TemplateData = Field(default_factory=dict)


class FlexlateDevConfig(BaseConfig):
    serve: ServeConfig = ServeConfig()
    _settings = AppConfig(
        app_name="flexlate-dev",
        default_format=ConfigFormats.YAML,
        config_name="flexlate-dev",
    )


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
