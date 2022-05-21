import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Callable, Union, Final

from gitignore_parser import parse_gitignore

ALWAYS_IGNORE: Final[List[str]] = [".git/"]


@dataclass
class IgnoreSpecification:
    ignore_list: List[str]
    _ignore_matches: Callable[[Union[str, Path]], bool] = field(init=False)

    def __post_init__(self):
        self._ignore_matches = self._build_ignore_matches()

    @property
    def all_ignores(self) -> List[str]:
        return [*ALWAYS_IGNORE, *self.ignore_list]

    def _build_ignore_matches(self) -> Callable[[str], bool]:
        return parse_gitignore_list_into_matcher(self.all_ignores)

    def file_is_ignored(self, file_path: Union[str, Path]) -> bool:
        return self._ignore_matches(file_path)


def parse_gitignore_list_into_matcher(
    gitignore_list: List[str],
) -> Callable[[Union[str, Path]], bool]:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        gitignore_path = temp_path / ".gitignore"
        gitignore_path.write_text("\n".join(gitignore_list) + "\n")
        base_matcher = parse_gitignore(gitignore_path, base_dir=temp_dir)

    def matcher(file_path: Union[str, Path]) -> bool:
        """
        Adjust the base_matcher from gitignore_parser so that relative paths are
        resolved in the temp directory.
        """
        full_path = temp_path / file_path
        return base_matcher(full_path)

    return matcher
