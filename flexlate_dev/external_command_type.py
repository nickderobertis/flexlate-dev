from enum import Enum


class ExternalCLICommandType(str, Enum):
    SERVE = "serve"
    PUBLISH = "publish"
