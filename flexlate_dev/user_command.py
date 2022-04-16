from typing import Optional

from pydantic import BaseModel, root_validator


class UserCommand(BaseModel):
    run: Optional[str] = None
    name: Optional[str] = None
    background: Optional[bool] = None
    id: Optional[str] = None

    @root_validator
    def run_or_id_must_be_defined(cls, v):
        if not v.get("run") and not v.get("id"):
            raise ValueError("run or id must be defined")
        return v

    @classmethod
    def from_string(cls, command: str) -> "UserCommand":
        return cls(run=command)

    @property
    def display_name(self) -> str:
        if self.name is None and self.run is None:
            raise ValueError("name or run must be defined")
        return self.name or self.run  # type: ignore

    @property
    def is_reference(self) -> bool:
        return self.id is not None and self.run is None
