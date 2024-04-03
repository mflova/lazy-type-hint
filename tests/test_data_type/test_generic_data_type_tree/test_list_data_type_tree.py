from typing import Any, Callable, Final, Iterable, List

import pytest

from lazy_type_hint.data_type_tree.generic_type import ListDataTypeTree
from lazy_type_hint.strategies import ParsingStrategies


class TestGetStrPy:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("Sequence", "list", "Union", "Any")
    """Imports that will be checked in case they were needed."""

    # fmt: off
    @pytest.mark.parametrize(
        "strategies",
        [
            (ParsingStrategies(list_strategy="list", min_height_to_define_type_alias=0)),
            (ParsingStrategies(list_strategy="Sequence", min_height_to_define_type_alias=0)),
        ],
    )
    @pytest.mark.parametrize(
        "data, expected_output, expected_n_children",
        [
            ([1], f"{NAME} = {{expected_container}}[int]", 1),
            ([1, 2], f"{NAME} = {{expected_container}}[int]", 1),
            ([1, 2.0], f"{NAME} = {{expected_container}}[float]", 2),
            ([{1, 2}, 2], f"{NAME} = {{expected_container}}[Union[{NAME}Set, int]]", 2),
            ([{1, 2}, [1, 2], {1, 3}, {1, 4}, [1, 2]], f"{NAME} = {{expected_container}}[Union[{NAME}List, {NAME}Set]]", 2),
            ([{1, 2}, {3, 4}], f"{NAME} = {{expected_container}}[{NAME}Set]", 1),
            ([{1, 2}, {3, 4.2}], f"{NAME} = {{expected_container}}[Union[{NAME}Set, {NAME}Set2]]", 2),
            ([{1, 2}, "a"], f"{NAME} = {{expected_container}}[Union[{NAME}Set, str]]", 2),
            ([{1, 2}, {"name": "Joan"}], f"{NAME} = {{expected_container}}[Union[{NAME}Dict, {NAME}Set]]", 2),
            ([], f"{NAME} = {{expected_container}}[Any]", 0),
        ],
    )
    # fmt: on
    def test_get_str_top_node(
        self,
        data: List[Any],
        strategies: ParsingStrategies,
        expected_output: str,
        expected_n_children: int,
        assert_imports: Callable[[ListDataTypeTree, Iterable[str]], None],
    ) -> None:
        """
        Test the `get_str_top_node` method of the `ListDataTypeTree` class.

        Args:
            data (List[Any]): The input data for the test.
            strategies (Strategies): The strategies object.
            expected_output (str): The expected output string.
            expected_n_children (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[ListDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.

        Returns:
            None: This method does not return anything.

        Raises:
            AssertionError: If the number of child nodes or the output string is not as expected.
        """
        tree = ListDataTypeTree(data, name=self.NAME, strategies=strategies)

        expected_output = expected_output.format(expected_container=strategies.list_strategy.capitalize())
        assert expected_n_children == len(tree), "Not all children were correctly parsed"
        assert expected_output == tree.get_str_top_node()
        assert_imports(tree, self.imports_to_check)


class TestTypeAliasHeight:
    NAME: Final = "Example"
    """Name that will be used to create the class."""

    @pytest.fixture
    def strategies(self, min_height: int) -> ParsingStrategies:
        return ParsingStrategies(min_height_to_define_type_alias=min_height)

    # fmt: off
    @pytest.mark.parametrize(
        "data, min_height, expected_str",
        [
            ([1], 0, f"{NAME} = List[int]"),
            ([1], 1, f"{NAME} = List[int]"),
            ([1], 2, f"{NAME} = List[int]"),
            ([1, [1]], 0, f"{NAME} = List[Union[{NAME}List, int]]"),
            ([1, [1]], 1, f"{NAME} = List[Union[List[int], int]]"),
        ],
    )
    # fmt: on
    def test_type_alias_based_on_height(
        self,
        data: List[Any],
        strategies: ParsingStrategies,
        expected_str: str,
        min_height: int,
    ) -> None:
        """
        Test the `get_str_top_node` method of the `ListDataTypeTree` class.

        Args:
            data (List[Any]): The input data for the test.
            strategies (Strategies): The strategies object.
            expected_str (str): The expected output string.
            min_height (int): The minimum height of the tree.
        """
        tree = ListDataTypeTree(data, name=self.NAME, strategies=strategies)
        assert expected_str == tree.get_str_top_node()
