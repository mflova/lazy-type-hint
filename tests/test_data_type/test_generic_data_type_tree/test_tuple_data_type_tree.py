from typing import Callable, Final, Iterable

import pytest

from dynamic_pyi_generator.data_type_tree.generic_type import TupleDataTypeTree
from dynamic_pyi_generator.strategies import Strategies


class TestGetStrPy:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("Tuple", "Union", "Any")
    """Imports that will be checked in case they were needed."""

    # fmt: off
    @pytest.mark.parametrize(
        "tree, expected_output, expected_n_childs",
        [
            # Fixed sice
            (TupleDataTypeTree((1,), name=NAME, strategies=Strategies(tuple_size_strategy="fixed")), f"{NAME} = Tuple[int]", 1),
            (TupleDataTypeTree((1, 2), name=NAME, strategies=Strategies(tuple_size_strategy="fixed")), f"{NAME} = Tuple[int, int]", 2),
            (TupleDataTypeTree((1, 2.0), name=NAME, strategies=Strategies(tuple_size_strategy="fixed")), f"{NAME} = Tuple[int, float]", 2),
            (TupleDataTypeTree(({1, 2}, 2), name=NAME, strategies=Strategies(tuple_size_strategy="fixed")), f"{NAME} = Tuple[{NAME}Set, int]", 2),
            (TupleDataTypeTree(((1,2), (1,2), (1,2)), name=NAME, strategies=Strategies(tuple_size_strategy="fixed")), f"{NAME} = Tuple[{NAME}Tuple, {NAME}Tuple2, {NAME}Tuple3]", 3),
            (TupleDataTypeTree(({1, 2}, {3, 4}), name=NAME, strategies=Strategies(tuple_size_strategy="fixed")), f"{NAME} = Tuple[{NAME}Set, {NAME}Set2]", 2),
            (TupleDataTypeTree(({1, 2}, {3, 4.2}), name=NAME, strategies=Strategies(tuple_size_strategy="fixed")), f"{NAME} = Tuple[{NAME}Set, {NAME}Set2]", 2),
            (TupleDataTypeTree(({1, 2}, "a"), name=NAME, strategies=Strategies(tuple_size_strategy="fixed")), f"{NAME} = Tuple[{NAME}Set, str]", 2),
            (TupleDataTypeTree(({1, 2}, {"name": "Joan"}), name=NAME, strategies=Strategies(tuple_size_strategy="fixed")), f"{NAME} = Tuple[{NAME}Set, {NAME}Dict]", 2),
            (TupleDataTypeTree((), name=NAME, strategies=Strategies(tuple_size_strategy="fixed")), f"{NAME} = Tuple[Any, ...]", 0),
            # Non fixed size
            (TupleDataTypeTree((1,), name=NAME, strategies=Strategies(tuple_size_strategy="...")), f"{NAME} = Tuple[int, ...]", 1),
            (TupleDataTypeTree((1, 2), name=NAME, strategies=Strategies(tuple_size_strategy="...")), f"{NAME} = Tuple[int, ...]", 1),
            (TupleDataTypeTree((1, 2.0), name=NAME, strategies=Strategies(tuple_size_strategy="...")), f"{NAME} = Tuple[float, ...]", 2),
            (TupleDataTypeTree(({1, 2}, 2), name=NAME, strategies=Strategies(tuple_size_strategy="...")), f"{NAME} = Tuple[Union[{NAME}Set, int], ...]", 2),
            (TupleDataTypeTree(((1,2), (1,2), (1,3)), name=NAME, strategies=Strategies(tuple_size_strategy="...")), f"{NAME} = Tuple[{NAME}Tuple, ...]", 1),
            (TupleDataTypeTree(({1, 2}, {3, 4}), name=NAME, strategies=Strategies(tuple_size_strategy="...")), f"{NAME} = Tuple[{NAME}Set, ...]", 1),
            (TupleDataTypeTree(({1, 2}, {3, 4.2}, {1}), name=NAME, strategies=Strategies(tuple_size_strategy="...")), f"{NAME} = Tuple[Union[{NAME}Set, {NAME}Set2], ...]", 2),
            (TupleDataTypeTree(({1, 2}, "a"), name=NAME, strategies=Strategies(tuple_size_strategy="...")), f"{NAME} = Tuple[Union[{NAME}Set, str], ...]", 2),
            (TupleDataTypeTree(({1, 2}, {"name": "Joan"}), name=NAME, strategies=Strategies(tuple_size_strategy="...")), f"{NAME} = Tuple[Union[{NAME}Dict, {NAME}Set], ...]", 2),
            (TupleDataTypeTree((), name=NAME, strategies=Strategies(tuple_size_strategy="...")), f"{NAME} = Tuple[Any, ...]", 0),
        ],
    )
    def test_get_str_py(
        self,
        tree: TupleDataTypeTree,
        expected_output: str,
        expected_n_childs: int,
        assert_imports: Callable[[TupleDataTypeTree, Iterable[str]], None],
    ) -> None:
        """
        Test the `get_str_py` method of the `TupleDataTypeTree` class.

        Args:
            tree (TupleDataTypeTree): An instance of the `TupleDataTypeTree` class.
            expected_output (str): The expected output string.
            expected_n_childs (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[TupleDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        assert expected_n_childs == len(tree), "Not all childs were correctly parsed"
        assert expected_output == tree.get_str_py()
        assert_imports(tree, self.imports_to_check)
