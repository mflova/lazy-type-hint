from collections.abc import Iterable
from typing import Any, Callable, Final

import pytest

from lazy_type_hint.data_type_tree.generic_type import SetDataTypeTree
from lazy_type_hint.strategies import ParsingStrategies


class TestGetStrPy:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("Any", "TypeAlias")
    """Imports that will be checked in case they were needed."""

    # fmt: off
    @pytest.mark.parametrize(
        "tree, expected_output, expected_n_children",
        [
            (SetDataTypeTree({1}, name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = set[int]", 1),
            (SetDataTypeTree({1, 2}, name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = set[int]", 1),
            (SetDataTypeTree({1, 2.0}, name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = set[float]", 2),
            (SetDataTypeTree({(1, 2), 2}, name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = set[Union[{NAME}Tuple, int]]", 2),
            (SetDataTypeTree({(1, 2), "a"}, name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = set[Union[{NAME}Tuple, str]]", 2),
            (SetDataTypeTree({(1, 2), (3, 4)}, name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = set[{NAME}Tuple]", 1),
            (SetDataTypeTree({(1, 2), (3, 4.2)}, name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = set[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree({(1, 2), (3, 4.2), (2, 3)}, name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = set[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree(set(), name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = set[Any]", 0),
            (SetDataTypeTree(frozenset({1}), name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = frozenset[int]", 1),
            (SetDataTypeTree(frozenset((1, 2)), name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = frozenset[int]", 1),
            (SetDataTypeTree(frozenset((1, 2.0)), name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = frozenset[float]", 2),
            (SetDataTypeTree(frozenset(((1, 2), 2)), name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = frozenset[Union[{NAME}Tuple, int]]", 2),
            (SetDataTypeTree(frozenset(((1, 2), "a")), name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = frozenset[Union[{NAME}Tuple, str]]", 2),
            (SetDataTypeTree(frozenset({(1, 2), (3, 4)}), name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = frozenset[{NAME}Tuple]", 1),
            (SetDataTypeTree(frozenset({(1, 2), (3, 4.2)}), name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = frozenset[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree(frozenset({(1, 2), (3, 4.2), (2, 3)}), name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = frozenset[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree(frozenset(set()), name=NAME, strategies=ParsingStrategies(min_depth_to_define_type_alias=0)), f"{NAME}: TypeAlias = frozenset[Any]", 0),
        ],
    )
    # fmt: on
    def test_get_str_top_node(
        self,
        tree: SetDataTypeTree,
        expected_output: str,
        expected_n_children: int,
        assert_imports: Callable[[SetDataTypeTree, Iterable[str]], None],
    ) -> None:
        """
        Test the `get_str_top_node` method of the `SetDataTypeTree` class.

        Args:
            tree (SetDataTypeTree): An instance of the `SetDataTypeTree` class.
            expected_output (str): The expected output string.
            expected_n_children (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[SetDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        assert expected_n_children == len(tree), "Not all children were correctly parsed"
        assert expected_output == tree.get_str_top_node()
        assert_imports(tree, self.imports_to_check)


class TestTypeAliasHeight:
    NAME: Final = "Example"
    """Name that will be used to create the class."""

    @pytest.fixture
    def strategies(self, min_height: int) -> ParsingStrategies:
        return ParsingStrategies(min_depth_to_define_type_alias=min_height)

    # fmt: off
    @pytest.mark.parametrize(
        "data, min_height, expected_str",
        [
            ({1}, 0, f"{NAME}: TypeAlias = set[int]"),
            ({1}, 1, f"{NAME}: TypeAlias = set[int]"),
            ({1}, 2, f"{NAME}: TypeAlias = set[int]"),
            ({1, frozenset({1})}, 0, f"{NAME}: TypeAlias = set[Union[{NAME}Frozenset, int]]"),
            ({1, frozenset({1})}, 1, f"{NAME}: TypeAlias = set[Union[frozenset[int], int]]"),
        ],
    )
    # fmt: on
    def test_type_alias_based_on_height(
        self,
        data: set[Any],
        strategies: ParsingStrategies,
        expected_str: str,
        min_height: int,
    ) -> None:
        """
        Test the `get_str_top_node` method of the `ListDataTypeTree` class.

        Args:
            data (list[Any]): The input data for the test.
            strategies (Strategies): The strategies object.
            expected_str (str): The expected output string.
            min_height (int): The minimum height of the tree.
        """
        tree = SetDataTypeTree(data, name=self.NAME, strategies=strategies)
        assert expected_str == tree.get_str_top_node()
