from types import MappingProxyType
from typing import Any, Callable, Final, Iterable, Mapping

import pytest

from dynamic_pyi_generator.data_type_tree.generic_type import DictDataTypeTree, MappingDataTypeTree
from dynamic_pyi_generator.strategies import Strategies
from dynamic_pyi_generator.utils import TAB


@pytest.mark.parametrize(
    "string, expected_out",
    (
        ["name_age", "NameAge"],
        ["a b", "AB"],
        ["Name$age", "NameAge"],
        ["2Name$age", "NameAge"],
    ),
)
def test_to_camel_case(string: str, expected_out: str) -> None:
    assert expected_out == MappingDataTypeTree._to_camel_case(string)


class TestGetStrPy:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("Mapping", "Any", "Dict", "TypedDict")
    """Imports that will be checked in case they were needed."""

    # fmt: off
    @pytest.mark.parametrize(
        "strategies",
        [
            (Strategies(dict_strategy="Dict")),
            (Strategies(dict_strategy="Mapping")),
        ],
    )
    @pytest.mark.parametrize(
        "data, expected_output, expected_n_childs",
        [
            ({"name": "Joan"}, f"{NAME} = {{expected_container}}[str, str]", 1),
            ({"age": 22}, f"{NAME} = {{expected_container}}[str, int]", 1),
            ({"name": "Joan", "age": 22}, f"{NAME} = {{expected_container}}[str, Union[int, str]]", 2),
            ({"name": "Joan", 21: 22}, f"{NAME} = {{expected_container}}[Union[int, str], Union[int, str]]", 2),
            ({22: "Joan", 21.2: 22}, f"{NAME} = {{expected_container}}[float, Union[int, str]]", 2),
            ({22: "Joan", 21.2: "number"}, f"{NAME} = {{expected_container}}[float, str]", 2),
            ({}, f"{NAME} = {{expected_container}}[Any, Any]", 0),
            (MappingProxyType({"name": "Joan"}), f"{NAME} = MappingProxyType[str, str]", 1),
            (MappingProxyType({"age": 22}), f"{NAME} = MappingProxyType[str, int]", 1),
            (MappingProxyType({"name": "Joan", "age": 22}), f"{NAME} = MappingProxyType[str, Union[int, str]]", 2),
            (MappingProxyType({"name": "Joan", 21: 22}), f"{NAME} = MappingProxyType[Union[int, str], Union[int, str]]", 2),
            (MappingProxyType({22: "Joan", 21.2: 22}), f"{NAME} = MappingProxyType[float, Union[int, str]]", 2),
            (MappingProxyType({22: "Joan", 21.2: "number"}), f"{NAME} = MappingProxyType[float, str]", 2),
            (MappingProxyType({}), f"{NAME} = MappingProxyType[Any, Any]", 0),
        ],
    )
    # fmt: on
    def test_get_str_py(
        self,
        data: Mapping[Any, Any],
        expected_output: str,
        expected_n_childs: int,
        strategies: Strategies,
        assert_imports: Callable[[MappingDataTypeTree, Iterable[str]], None],
    ) -> None:
        """
        Test the `get_str_py` method of the `DictDataTypeTree` class.

        Args:
            data (Mapping[Any, Any]): The input data for the test.
            expected_output (str): The expected output string.
            expected_n_childs (int): The expected number of child nodes in the tree.
            strategies (Strategies): The strategies object.
            assert_imports (Callable[[DictDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        tree: MappingDataTypeTree
        if isinstance(data, dict):
            tree = DictDataTypeTree(data, name=self.NAME, strategies=strategies)
        else:
            tree = MappingDataTypeTree(data, name=self.NAME, strategies=strategies)

        expected_output = expected_output.format(expected_container=strategies.dict_strategy)
        assert expected_n_childs == len(tree), "Not all childs were correctly parsed"
        assert expected_output == tree.get_str_py()
        assert_imports(tree, self.imports_to_check)

    @pytest.mark.parametrize(
        "tree, expected_output, expected_n_childs",
        [
            (
                DictDataTypeTree({"name": "Joan"}, name=NAME),
                f"""class {NAME}(TypedDict):
{TAB}name: str""",
                1,
            ),
            (
                DictDataTypeTree({"age": 22}, name=NAME),
                f"""class {NAME}(TypedDict):
{TAB}age: int""",
                1,
            ),
            (
                DictDataTypeTree({"name": "Joan", "age": 21}, name=NAME),
                f"""class {NAME}(TypedDict):
{TAB}name: str
{TAB}age: int""",
                2,
            ),
            (
                DictDataTypeTree({"name": "Joan", "kids": ["A", "B"]}, name=NAME),
                f"""class {NAME}(TypedDict):
{TAB}name: str
{TAB}kids: {NAME}Kids""",
                2,
            ),
            (
                DictDataTypeTree({"name": "Joan", "kids": ["A", "B"], "parents": ["C", "D"]}, name=NAME),
                f"""class {NAME}(TypedDict):
{TAB}name: str
{TAB}kids: {NAME}Kids
{TAB}parents: {NAME}Parents""",
                3,
            ),
        ],
    )
    def test_get_str_typed_dict_py(
        self,
        tree: DictDataTypeTree,
        expected_output: str,
        expected_n_childs: int,
        assert_imports: Callable[[DictDataTypeTree, Iterable[str]], None],
    ) -> None:
        """
        Test the `get_str_py` method of the `DictDataTypeTree` class.

        Args:
            tree (TupleDataTypeTree): An instance of the `TupleDataTypeTree` class.
            expected_output (str): The expected output string.
            expected_n_childs (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[TupleDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        assert expected_n_childs == len(tree), "Not all childs were correctly parsed"
        assert expected_output == tree.get_str_py()
        assert_imports(tree, self.imports_to_check)

    @pytest.mark.parametrize(
        "tree, expected_output, expected_n_childs",
        [
            (
                DictDataTypeTree({"name and surname": "Joan B."}, name=NAME),
                f"""{NAME} = TypedDict(
    "{NAME}",
    {{
        "name and surname": str,
    }},
)""",
                1,
            ),
            (
                DictDataTypeTree({"$": 22.0, "own_list": [1, 2, 3]}, name=NAME),
                f"""{NAME} = TypedDict(
    "{NAME}",
    {{
        "$": float,
        "own_list": {NAME}OwnList,
    }},
)""",
                2,
            ),
            (
                DictDataTypeTree({"$": 22, "my_list": [1, 2, 3], "my_list2": [2, 3]}, name=NAME),
                f"""{NAME} = TypedDict(
    "{NAME}",
    {{
        "$": int,
        "my_list": {NAME}MyList,
        "my_list2": {NAME}MyList2,
    }},
)""",
                3,
            ),
        ],
    )
    def test_get_str_typed_dict_functional_syntax_py(
        self,
        tree: DictDataTypeTree,
        expected_output: str,
        expected_n_childs: int,
        assert_imports: Callable[[DictDataTypeTree, Iterable[str]], None],
    ) -> None:
        """
        Test the `get_str_py` method of the `DictDataTypeTree` class.

        Args:
            tree (TupleDataTypeTree): An instance of the `TupleDataTypeTree` class.
            expected_output (str): The expected output string.
            expected_n_childs (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[TupleDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        assert expected_n_childs == len(tree), "Not all childs were correctly parsed"
        assert expected_output == tree.get_str_py()
        assert_imports(tree, self.imports_to_check)
