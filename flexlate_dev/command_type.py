from enum import Enum


class CommandType(str, Enum):
    SERVE = "serve"
    PUBLISH = "publish"
