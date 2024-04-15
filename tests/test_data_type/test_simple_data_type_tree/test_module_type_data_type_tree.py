from typing import Final

import pytest

from lazy_type_hint.data_type_tree.simple_data_type_tree.module_data_type_tree import ModuleTypeDataTypeTree


class TestModuleType:
    NAME: Final = "Example"

    def test_get_str_top_node(self) -> None:
        tree = ModuleTypeDataTypeTree(pytest, self.NAME)
        assert f"{self.NAME} = ModuleType" == tree.get_str_top_node()
        assert "ModuleType" in tree.imports
