import io
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Callable

from pydantic import BaseModel
from gitignore_parser import parse_gitignore


@dataclass
class IgnoreSpecification:
    ignore_list: List[str]
    base_dir: Path
    _ignore_matches: Callable[[str], bool] = field(init=False)

    def __post_init__(self):
        self._ignore_matches = self._build_ignore_matches()

    def _build_ignore_matches(self) -> Callable[[str], bool]:
        return parse_gitignore_list_into_matcher(self.ignore_list, self.base_dir)

    def file_is_ignored(self, file_path: str) -> bool:
        return self._ignore_matches(file_path)


def parse_gitignore_list_into_matcher(
    gitignore_list: List[str], base_dir: Path
) -> Callable[[str], bool]:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / ".gitignore"
        temp_path.write_text("\n".join(gitignore_list) + "\n")
        matcher = parse_gitignore(temp_path, base_dir=base_dir)
    return matcher
