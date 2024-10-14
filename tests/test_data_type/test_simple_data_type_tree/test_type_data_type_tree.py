from typing import Any, Final

import pytest

from lazy_type_hint.data_type_tree.simple_data_type_tree.type_data_type_tree import TypeDataTypeTree


class DummyClass:
    ...


class TestTypes:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "data, expected_str",
        [
            (DummyClass, f'{NAME}: TypeAlias = type["DummyClass"]'),
            (bool, f"{NAME}: TypeAlias = type[bool]"),
            (int, f"{NAME}: TypeAlias = type[int]"),
        ],
    )
    def test_types(self, data: Any, expected_str: str) -> None:
        data_type_tree = TypeDataTypeTree(data, self.NAME)
        assert expected_str == data_type_tree.get_str_top_node()
        assert "TypeAlias" in data_type_tree.imports
