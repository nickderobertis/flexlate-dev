from typing import Optional

from pydantic import BaseModel


class UserCommand(BaseModel):
    run: str
    name: Optional[str] = None
    background: Optional[bool] = None

    @classmethod
    def from_string(cls, command: str) -> "UserCommand":
        return cls(run=command)

    @property
    def display_name(self) -> str:
        return self.name or self.run
