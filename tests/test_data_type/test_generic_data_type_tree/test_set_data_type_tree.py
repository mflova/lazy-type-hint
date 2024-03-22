from typing import Callable, Final, Iterable

import pytest

from dynamic_pyi_generator.data_type_tree.generic_type import SetDataTypeTree


class TestGetStrPy:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("Set", "FrozenSet", "Any")
    """Imports that will be checked in case they were needed."""

    # fmt: off
    @pytest.mark.parametrize(
        "tree, expected_output, expected_n_childs",
        [
            (SetDataTypeTree({1}, name=NAME), f"{NAME} = Set[int]", 1),
            (SetDataTypeTree({1, 2}, name=NAME), f"{NAME} = Set[int]", 1),
            (SetDataTypeTree({1, 2.0}, name=NAME), f"{NAME} = Set[float]", 2),
            (SetDataTypeTree({(1, 2), 2}, name=NAME), f"{NAME} = Set[Union[{NAME}Tuple, int]]", 2),
            (SetDataTypeTree({(1, 2), "a"}, name=NAME), f"{NAME} = Set[Union[{NAME}Tuple, str]]", 2),
            (SetDataTypeTree({(1, 2), (3, 4)}, name=NAME), f"{NAME} = Set[{NAME}Tuple]", 1),
            (SetDataTypeTree({(1, 2), (3, 4.2)}, name=NAME), f"{NAME} = Set[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree({(1, 2), (3, 4.2), (2, 3)}, name=NAME), f"{NAME} = Set[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree(set(), name=NAME), f"{NAME} = Set[Any]", 0),
            (SetDataTypeTree(frozenset({1}), name=NAME), f"{NAME} = FrozenSet[int]", 1),
            (SetDataTypeTree(frozenset((1, 2)), name=NAME), f"{NAME} = FrozenSet[int]", 1),
            (SetDataTypeTree(frozenset((1, 2.0)), name=NAME), f"{NAME} = FrozenSet[float]", 2),
            (SetDataTypeTree(frozenset(((1, 2), 2)), name=NAME), f"{NAME} = FrozenSet[Union[{NAME}Tuple, int]]", 2),
            (SetDataTypeTree(frozenset(((1, 2), "a")), name=NAME), f"{NAME} = FrozenSet[Union[{NAME}Tuple, str]]", 2),
            (SetDataTypeTree(frozenset({(1, 2), (3, 4)}), name=NAME), f"{NAME} = FrozenSet[{NAME}Tuple]", 1),
            (SetDataTypeTree(frozenset({(1, 2), (3, 4.2)}), name=NAME), f"{NAME} = FrozenSet[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree(frozenset({(1, 2), (3, 4.2), (2, 3)}), name=NAME), f"{NAME} = FrozenSet[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree(frozenset(set()), name=NAME), f"{NAME} = FrozenSet[Any]", 0),
        ],
    )
    # fmt: on
    def test_get_str_py(
        self,
        tree: SetDataTypeTree,
        expected_output: str,
        expected_n_childs: int,
        assert_imports: Callable[[SetDataTypeTree, Iterable[str]], None],
    ) -> None:
        """
        Test the `get_str_py` method of the `SetDataTypeTree` class.

        Args:
            tree (SetDataTypeTree): An instance of the `SetDataTypeTree` class.
            expected_output (str): The expected output string.
            expected_n_childs (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[SetDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        assert expected_n_childs == len(tree), "Not all childs were correctly parsed"
        assert expected_output == tree.get_str_py()
        assert_imports(tree, self.imports_to_check)
