from typing import Any, Callable, Final, Iterable, Set

import pytest

from dynamic_pyi_generator.data_type_tree.generic_type import SetDataTypeTree
from dynamic_pyi_generator.strategies import Strategies


class TestGetStrPy:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("set", "FrozenSet", "Any")
    """Imports that will be checked in case they were needed."""

    # fmt: off
    @pytest.mark.parametrize(
        "tree, expected_output, expected_n_childs",
        [
            (SetDataTypeTree({1}, name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = Set[int]", 1),
            (SetDataTypeTree({1, 2}, name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = Set[int]", 1),
            (SetDataTypeTree({1, 2.0}, name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = Set[float]", 2),
            (SetDataTypeTree({(1, 2), 2}, name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = Set[Union[{NAME}Tuple, int]]", 2),
            (SetDataTypeTree({(1, 2), "a"}, name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = Set[Union[{NAME}Tuple, str]]", 2),
            (SetDataTypeTree({(1, 2), (3, 4)}, name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = Set[{NAME}Tuple]", 1),
            (SetDataTypeTree({(1, 2), (3, 4.2)}, name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = Set[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree({(1, 2), (3, 4.2), (2, 3)}, name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = Set[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree(set(), name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = Set[Any]", 0),
            (SetDataTypeTree(frozenset({1}), name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = FrozenSet[int]", 1),
            (SetDataTypeTree(frozenset((1, 2)), name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = FrozenSet[int]", 1),
            (SetDataTypeTree(frozenset((1, 2.0)), name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = FrozenSet[float]", 2),
            (SetDataTypeTree(frozenset(((1, 2), 2)), name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = FrozenSet[Union[{NAME}Tuple, int]]", 2),
            (SetDataTypeTree(frozenset(((1, 2), "a")), name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = FrozenSet[Union[{NAME}Tuple, str]]", 2),
            (SetDataTypeTree(frozenset({(1, 2), (3, 4)}), name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = FrozenSet[{NAME}Tuple]", 1),
            (SetDataTypeTree(frozenset({(1, 2), (3, 4.2)}), name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = FrozenSet[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree(frozenset({(1, 2), (3, 4.2), (2, 3)}), name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = FrozenSet[Union[{NAME}Tuple, {NAME}Tuple2]]", 2),
            (SetDataTypeTree(frozenset(set()), name=NAME, strategies=Strategies(min_height_to_define_type_alias=0)), f"{NAME} = FrozenSet[Any]", 0),
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


class TestTypeAliasHeight:
    NAME: Final = "Example"
    """Name that will be used to create the class."""

    @pytest.fixture
    def strategies(self, min_height: int) -> Strategies:
        return Strategies(min_height_to_define_type_alias=min_height)

    # fmt: off
    @pytest.mark.parametrize(
        "data, min_height, expected_str",
        [
            ({1}, 0, f"{NAME} = Set[int]"),
            ({1}, 1, f"{NAME} = Set[int]"),
            ({1}, 2, f"{NAME} = Set[int]"),
            ({1, frozenset({1})}, 0, f"{NAME} = Set[Union[{NAME}Frozenset, int]]"),
            ({1, frozenset({1})}, 1, f"{NAME} = Set[Union[FrozenSet[int], int]]"),
        ],
    )
    # fmt: on
    def test_type_alias_based_on_height(
        self,
        data: Set[Any],
        strategies: Strategies,
        expected_str: str,
        min_height: int,  # noqa: ARG002
    ) -> None:
        """
        Test the `get_str_py` method of the `ListDataTypeTree` class.

        Args:
            data (List[Any]): The input data for the test.
            strategies (Strategies): The strategies object.
            expected_str (str): The expected output string.
            min_height (int): The minimum height of the tree.
        """
        tree = SetDataTypeTree(data, name=self.NAME, strategies=strategies)
        assert expected_str == tree.get_str_py()
