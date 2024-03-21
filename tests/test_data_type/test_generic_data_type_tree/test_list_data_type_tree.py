from typing import Any, Callable, Final, Iterable, List

import pytest

from dynamic_pyi_generator.data_type_tree.generic_type import ListDataTypeTree
from dynamic_pyi_generator.strategies import Strategies


class TestGetStrPy:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("Sequence", "List", "Union", "Any")
    """Imports that will be checked in case they were needed."""

    # fmt: off
    @pytest.mark.parametrize(
        "strategies",
        [
            (Strategies(list_strategy="List")),
            (Strategies(list_strategy="Sequence")),
        ],
    )
    @pytest.mark.parametrize(
        "data, expected_output, expected_n_childs",
        [
            ([1], f"{NAME} = {{expected_container}}[int]", 1),
            ([1, 2], f"{NAME} = {{expected_container}}[int]", 2),
            ([1, 2.0], f"{NAME} = {{expected_container}}[float]", 2),
            ([{1, 2}, 2], f"{NAME} = {{expected_container}}[Union[{NAME}Set, int]]", 2),
            ([{1, 2}, [1, 2], {1, 3}, {1, 4}, [1, 2]], f"{NAME} = {{expected_container}}[Union[{NAME}List, {NAME}List2, {NAME}Set, {NAME}Set2, {NAME}Set3]]" ,5),
            ([{1, 2}, {3, 4}], f"{NAME} = {{expected_container}}[Union[{NAME}Set, {NAME}Set2]]", 2),
            ([{1, 2}, {3, 4.2}], f"{NAME} = {{expected_container}}[Union[{NAME}Set, {NAME}Set2]]", 2),
            ([{1, 2}, "a"], f"{NAME} = {{expected_container}}[Union[{NAME}Set, str]]", 2),
            ([{1, 2}, {"name": "Joan"}], f"{NAME} = {{expected_container}}[Union[{NAME}Dict, {NAME}Set]]", 2),
            ([], f"{NAME} = {{expected_container}}[Any]", 0),
        ],
    )
    # fmt: on
    def test_get_str_py(
        self,
        data: List[Any],
        strategies: Strategies,
        expected_output: str,
        expected_n_childs: int,
        assert_imports: Callable[[ListDataTypeTree, Iterable[str]], None],
    ) -> None:
        """
        Test the `get_str_py` method of the `ListDataTypeTree` class.

        Args:
            data (List[Any]): The input data for the test.
            strategies (Strategies): The strategies object.
            expected_output (str): The expected output string.
            expected_n_childs (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[ListDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.

        Returns:
            None: This method does not return anything.

        Raises:
            AssertionError: If the number of child nodes or the output string is not as expected.
        """
        tree = ListDataTypeTree(data, name=self.NAME, strategies=strategies)

        expected_output = expected_output.format(expected_container=strategies.list_strategy)
        assert expected_n_childs == len(tree), "Not all childs were correctly parsed"
        assert expected_output == tree.get_str_py()
        assert_imports(tree, self.imports_to_check)
