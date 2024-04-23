from typing import Final

import pytest

from lazy_type_hint.data_type_tree.simple_data_type_tree.instance_data_type_tree import InstanceDataTypeTree


class DummyClass:
    ...


class TestGetStrPy:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "data, expected_str",
        [
            [range(1, 2), f"{NAME}: TypeAlias = range"],
            [slice(1, 2), f"{NAME}: TypeAlias = slice"],
            [True, f"{NAME}: TypeAlias = bool"],
            [False, f"{NAME}: TypeAlias = bool"],
            ["random_string", f"{NAME}: TypeAlias = str"],
            [5, f"{NAME}: TypeAlias = int"],
            [6.7, f"{NAME}: TypeAlias = float"],
        ],
    )
    def test_get_str_top_node(self, data: object, expected_str: str) -> None:
        data_type_tree = InstanceDataTypeTree(data, self.NAME)
        assert expected_str == data_type_tree.get_str_top_node()

    def test_none(self) -> None:
        data_type_tree = InstanceDataTypeTree(None, self.NAME)
        assert f"{self.NAME}: TypeAlias = Optional[object]" == data_type_tree.get_str_top_node()
        assert "Optional" in data_type_tree.imports
        assert "TypeAlias" in data_type_tree.imports

    def test_custom_class(self) -> None:
        data_type_tree = InstanceDataTypeTree(DummyClass(), self.NAME)
        assert f'{self.NAME}: TypeAlias = "DummyClass"' == data_type_tree.get_str_top_node()
        assert "TypeAlias" in data_type_tree.imports


class TestHash:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "tree1, tree2, expected_output",
        [
            [InstanceDataTypeTree(range(3, 4), name="Data1"), InstanceDataTypeTree(range(1, 2), name="Data2"), True],
            [InstanceDataTypeTree(slice(3, 4), name="Data1"), InstanceDataTypeTree(slice(1, 2), name="Data2"), True],
            [InstanceDataTypeTree(True, name="Data1"), InstanceDataTypeTree(True, name="Data2"), True],
            [InstanceDataTypeTree(False, name="Data1"), InstanceDataTypeTree(True, name="Data2"), True],
            [InstanceDataTypeTree(False, name="Data1"), InstanceDataTypeTree(False, name="Data2"), True],
            [InstanceDataTypeTree("string1", name="Data1"), InstanceDataTypeTree("string2", name="Data2"), True],
            [InstanceDataTypeTree(5, name="Data1"), InstanceDataTypeTree(7, name="Data2"), True],
            [InstanceDataTypeTree(5.2, name="Data1"), InstanceDataTypeTree(7.1, name="Data2"), True],
            [InstanceDataTypeTree(range(1, 2), name="Data1"), InstanceDataTypeTree(7, name="Data1"), False],
            [InstanceDataTypeTree(range(1, 2), name="Data1"), InstanceDataTypeTree(slice(2.7), name="Data1"), False],
            [InstanceDataTypeTree(5.2, name="Data1"), InstanceDataTypeTree("str", name="Data2"), False],
        ],
    )
    def test_get_str_top_node(
        self, tree1: InstanceDataTypeTree, tree2: InstanceDataTypeTree, expected_output: bool
    ) -> None:
        assert expected_output == (hash(tree1) == hash(tree2))
