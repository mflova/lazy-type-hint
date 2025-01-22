from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import Any, Callable, Final

import pytest

from lazy_type_hint.data_type_tree.generic_type import DictDataTypeTree, MappingDataTypeTree
from lazy_type_hint.file_modifiers.yaml_file_modifier import YamlFileModifier
from lazy_type_hint.strategies import ParsingStrategies


@pytest.mark.parametrize(
    "string, expected_out",
    (
        ["name_age", "NameAge"],
        ["a b", "AB"],
        ["Name$age", "NameAge"],
        ["2Name$age", "NameAge"],
        [str(2), "2"],
    ),
)
def test_to_camel_case(string: str, expected_out: str) -> None:
    assert expected_out == MappingDataTypeTree._to_camel_case(string)


class TestGetStrPy:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("Mapping", "Any", "TypedDict", "MappingProxyType")
    """Imports that will be checked in case they were needed."""

    # fmt: off
    @pytest.mark.parametrize(
        "strategies",
        [
            (ParsingStrategies(dict_strategy="dict", min_depth_to_define_type_alias=0)),
            (ParsingStrategies(dict_strategy="Mapping", min_depth_to_define_type_alias=0)),
        ],
    )
    @pytest.mark.parametrize(
        "data, expected_output, expected_n_children",
        [
            ({"name": "Joan"}, f"{NAME}: TypeAlias = {{expected_container}}[str, str]", 1),
            ({"age": 22}, f"{NAME}: TypeAlias = {{expected_container}}[str, int]", 1),
            ({"name": "Joan", "age": 22}, f"{NAME}: TypeAlias = {{expected_container}}[str, Union[int, str]]", 2),
            ({"name": "Joan", 21: 22}, f"{NAME}: TypeAlias = {{expected_container}}[Union[int, str], Union[int, str]]", 2),
            ({22: "Joan", 21.2: 22}, f"{NAME}: TypeAlias = {{expected_container}}[float, Union[int, str]]", 2),
            ({22: "Joan", 21.2: "number"}, f"{NAME}: TypeAlias = {{expected_container}}[float, str]", 2),
            ({}, f"{NAME}: TypeAlias = {{expected_container}}[Any, Any]", 0),
            (MappingProxyType({"name": "Joan"}), f"{NAME}: TypeAlias = MappingProxyType[str, str]", 1),
            (MappingProxyType({"age": 22}), f"{NAME}: TypeAlias = MappingProxyType[str, int]", 1),
            (MappingProxyType({"name": "Joan", "age": 22}), f"{NAME}: TypeAlias = MappingProxyType[str, Union[int, str]]", 2),
            (MappingProxyType({"name": "Joan", 21: 22}), f"{NAME}: TypeAlias = MappingProxyType[Union[int, str], Union[int, str]]", 2),
            (MappingProxyType({22: "Joan", 21.2: 22}), f"{NAME}: TypeAlias = MappingProxyType[float, Union[int, str]]", 2),
            (MappingProxyType({22: "Joan", 21.2: "number"}), f"{NAME}: TypeAlias = MappingProxyType[float, str]", 2),
            (MappingProxyType({}), f"{NAME}: TypeAlias = MappingProxyType[Any, Any]", 0),
        ],
    )
    # fmt: on
    def test_get_str_top_node(
        self,
        data: Mapping[Any, Any],
        expected_output: str,
        expected_n_children: int,
        strategies: ParsingStrategies,
        assert_imports: Callable[[MappingDataTypeTree, Iterable[str]], None],
    ) -> None:
        """
        Test the `get_str_top_node` method of the `DictDataTypeTree` class.

        Args:
            data (Mapping[Any, Any]): The input data for the test.
            expected_output (str): The expected output string.
            expected_n_children (int): The expected number of child nodes in the tree.
            strategies (Strategies): The strategies object.
            assert_imports (Callable[[DictDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        tree: MappingDataTypeTree
        if isinstance(data, dict):
            tree = DictDataTypeTree(data, name=self.NAME, strategies=strategies)
        else:
            tree = MappingDataTypeTree(data, name=self.NAME, strategies=strategies)

        expected_output = expected_output.format(expected_container=strategies.dict_strategy)
        assert expected_n_children == len(tree), "Not all children were correctly parsed"
        assert expected_output == tree.get_str_top_node()
        assert_imports(tree, self.imports_to_check)


class TestGetAliasHeight:
    NAME: Final = "Example"
    """Name that will be used to create the class."""

    # fmt: off
    @pytest.mark.parametrize(
        "data, min_height, expected_output",
        [
            ({"name": {"unit": "dolar"}}, 0, f"{NAME}: TypeAlias = dict[str, ExampleName]"),
            ({"name": {"unit": "dolar"}}, 1, f"{NAME}: TypeAlias = dict[str, dict[str, str]]"),
            ({"name": {"unit": "dolar"}}, 2, f"{NAME}: TypeAlias = dict[str, dict[str, str]]"),
        ],
    )
    # fmt: on
    def test_type_alias_based_on_height(self, data: Mapping[Any, Any], expected_output: str, min_height: int) -> None:
        """
        Test the `get_str_top_node` method of the `DictDataTypeTree` class.

        Args:
            data (Mapping[Any, Any]): The input data for the test.
            expected_output (str): The expected output string.
            min_height (int): The minimum height to define the type alias.
        """
        tree = DictDataTypeTree(
            data,
            name=self.NAME,
            strategies=ParsingStrategies(min_depth_to_define_type_alias=min_height, dict_strategy="dict"),
        )
        assert expected_output == tree.get_str_top_node()


class TestHiddenKeyBasedDocs:
    PREFIX: Final = YamlFileModifier.prefix

    @pytest.mark.parametrize(
        "data1, data2, expected_same_hash",
        [
            (
                MappingProxyType({"name": "Joan", f"{PREFIX}name": "This is a doc"}),
                MappingProxyType({"name": "Joan"}),
                True,
            ),
            (MappingProxyType({"age": 22, f"{PREFIX}age": "This is a doc"}), MappingProxyType({"age": 23}), True),
            (MappingProxyType({"age": 22, f"{PREFIX}age": "This is a doc"}), MappingProxyType({"age": "22"}), False),
        ],
    )
    def test_hash_is_not_altered(
        self, data1: Mapping[Any, Any], data2: Mapping[Any, Any], expected_same_hash: bool
    ) -> None:
        tree1 = MappingDataTypeTree(data1, name="Tree1")
        tree2 = MappingDataTypeTree(data2, name="Tree2")
        assert expected_same_hash == (hash(tree1) == hash(tree2))

    @pytest.mark.parametrize(
        "data1, data2",
        [
            (MappingProxyType({"name": "Joan", f"{PREFIX}name": "This is a doc"}), MappingProxyType({"name": "Joan"})),
            (MappingProxyType({"age": 22, f"{PREFIX}age": "This is a doc"}), MappingProxyType({"age": 23})),
        ],
    )
    def test_type_alias_does_not_change(self, data1: Mapping[Any, Any], data2: Mapping[Any, Any]) -> None:
        tree1 = MappingDataTypeTree(data1, name="Tree1")
        tree2 = MappingDataTypeTree(data2, name="Tree2")
        assert tree1.get_str_top_node_without_lvalue() == tree2.get_str_top_node_without_lvalue()
