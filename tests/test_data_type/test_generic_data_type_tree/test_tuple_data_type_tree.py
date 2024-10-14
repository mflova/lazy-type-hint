from typing import Callable, Final
from collections.abc import Iterable

import pytest

from lazy_type_hint.data_type_tree.generic_type import TupleDataTypeTree
from lazy_type_hint.strategies import ParsingStrategies


class TestGetStrPy:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("Union", "Any", "TypeAlias")
    """Imports that will be checked in case they were needed."""

    # fmt: off
    @pytest.mark.parametrize(
        "tree, expected_output, expected_n_children",
        [
            # Fixed sice
            (TupleDataTypeTree((1,), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[int]", 1),
            (TupleDataTypeTree((1, 2), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[int, int]", 2),
            (TupleDataTypeTree((1, 2.0), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[int, float]", 2),
            (TupleDataTypeTree(({1, 2}, 2), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[{NAME}Set, int]", 2),
            (TupleDataTypeTree(((1,2), (1,2), (1,2)), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[{NAME}Tuple, {NAME}Tuple, {NAME}Tuple]", 3),
            (TupleDataTypeTree(({1, 2}, {3, 4}), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[{NAME}Set, {NAME}Set]", 2),
            (TupleDataTypeTree(({1, 2}, {3, 4.2}), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[{NAME}Set, {NAME}Set2]", 2),
            (TupleDataTypeTree(({1, 2}, "a"), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[{NAME}Set, str]", 2),
            (TupleDataTypeTree(({1, 2}, {"name": "Joan"}), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[{NAME}Set, {NAME}Dict]", 2),
            (TupleDataTypeTree((), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[Any, ...]", 0),
            # Non fixed size
            (TupleDataTypeTree((1,), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="any size", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[int, ...]", 1),
            (TupleDataTypeTree((1, 2), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="any size", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[int, ...]", 1),
            (TupleDataTypeTree((1, 2.0), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="any size", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[float, ...]", 2),
            (TupleDataTypeTree(({1, 2}, 2), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="any size", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[Union[{NAME}Set, int], ...]", 2),
            (TupleDataTypeTree(((1,2), (1,2), (1,3)), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="any size", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[{NAME}Tuple, ...]", 1),
            (TupleDataTypeTree(({1, 2}, {3, 4}), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="any size", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[{NAME}Set, ...]", 1),
            (TupleDataTypeTree(({1, 2}, {3, 4.2}, {1}), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="any size", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[Union[{NAME}Set, {NAME}Set2], ...]", 2),
            (TupleDataTypeTree(({1, 2}, "a"), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="any size", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[Union[{NAME}Set, str], ...]", 2),
            (TupleDataTypeTree(({1, 2}, {"name": "Joan"}), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="any size", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[Union[{NAME}Dict, {NAME}Set], ...]", 2),
            (TupleDataTypeTree((), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="any size", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[Any, ...]", 0),
        ],
    )
    def test_get_str_top_node(
        self,
        tree: TupleDataTypeTree,
        expected_output: str,
        expected_n_children: int,
        assert_imports: Callable[[TupleDataTypeTree, Iterable[str]], None],
    ) -> None:
        """
        Test the `get_str_top_node` method of the `TupleDataTypeTree` class.

        Args:
            tree (TupleDataTypeTree): An instance of the `TupleDataTypeTree` class.
            expected_output (str): The expected output string.
            expected_n_children (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[TupleDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        assert expected_n_children == len(tree), "Not all children were correctly parsed"
        assert expected_output == tree.get_str_top_node()
        assert_imports(tree, self.imports_to_check)


class TestTypeAliasHeight:
    NAME: Final = "Example"
    """Name that will be used to create the class."""

    @pytest.fixture
    def strategies(self, min_height: int) -> ParsingStrategies:
        return ParsingStrategies(min_height_to_define_type_alias=min_height)


class TestGetAliasHeight:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("tuple", "Union", "Any", "TypeAlias")
    """Imports that will be checked in case they were needed."""

    # fmt: off
    @pytest.mark.parametrize(
        "tree, expected_str",
        [
            # Fixed sice
            (TupleDataTypeTree(((1, 2), 2), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[{NAME}Tuple, int]"),
            (TupleDataTypeTree(((1, 2), 2), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=1)), f"{NAME}: TypeAlias = tuple[tuple[int, int], int]"),
            (TupleDataTypeTree(((1, (1, "str")), 2), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=0)), f"{NAME}: TypeAlias = tuple[ExampleTuple, int]"),
            (TupleDataTypeTree(((1, (1, "str")), 2), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=1)), f"{NAME}: TypeAlias = tuple[ExampleTuple, int]"),
            (TupleDataTypeTree(((1, (1, "str")), 2), name=NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed", min_height_to_define_type_alias=2)), f"{NAME}: TypeAlias = tuple[tuple[int, tuple[int, str]], int]"),
        ],
    )
    def test_type_alias_based_on_height(
            self,
            tree: TupleDataTypeTree,
            expected_str: str,
        ) -> None:
            """
            Test the `get_str_top_node` method of the `TupleDataTypeTree` class.

            Args:
                tree (TupleDataTypeTree): An instance of the `TupleDataTypeTree` class.
                expected_str (str): The expected output string.
            """
            # Reminder: `get_str_top_node` does not work in a recursive manner
            assert expected_str == tree.get_str_top_node()
