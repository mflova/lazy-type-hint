from collections.abc import Iterator
from typing import Any, Final

import pytest

from lazy_type_hint.data_type_tree.generic_type.iterator_data_type_tree import IteratorDataTypeTree
from lazy_type_hint.strategies import ParsingStrategies


class TestIterator:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "data, expected_str",
        [
            (iter([1, 2, 3]), f"{NAME}: TypeAlias = Iterator[int]"),
            (iter(["1", 2]), f"{NAME}: TypeAlias = Iterator[Union[int, str]]"),
            (iter(["1", [1, 2]]), f"{NAME}: TypeAlias = Iterator[Union[{NAME}List, str]]"),
        ],
    )
    def test_get_str_top_node(self, data: Iterator[Any], expected_str: str) -> None:
        tree = IteratorDataTypeTree(
            data, name="Example", strategies=ParsingStrategies(min_depth_to_define_type_alias=0)
        )
        assert expected_str == tree.get_str_top_node()
        assert "Iterator" in tree.imports
        assert "TypeAlias" in tree.imports
