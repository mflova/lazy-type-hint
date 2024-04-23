from pathlib import Path
from typing import Final

from lazy_type_hint.data_type_tree.simple_data_type_tree.io_data_type_tree import IoDataTypeTree


class TestModuleType:
    NAME: Final = "Example"

    def test_get_str_top_node(self, tmp_path: str) -> None:
        f = open(Path(tmp_path) / "temp.tmp", mode="w")
        tree = IoDataTypeTree(f, self.NAME)
        assert f"{self.NAME}: TypeAlias = TextIO" == tree.get_str_top_node()
        assert "TextIO" in tree.imports
        assert "TypeAlias" in tree.imports
