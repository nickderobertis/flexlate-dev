from typing import Optional

from pydantic import BaseModel


class UserCommand(BaseModel):
    run: str
    name: Optional[str] = None
    background: bool = False

    @classmethod
    def from_string(cls, command: str) -> "UserCommand":
        return cls(run=command)
