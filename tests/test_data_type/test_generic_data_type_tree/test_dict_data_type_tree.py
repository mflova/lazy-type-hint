from copy import deepcopy
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Hashable,
    Iterable,
    List,
    Mapping,
    Sequence,
    Set,
    Sized,
    Tuple,
)

import pytest

from dynamic_pyi_generator.data_type_tree import data_type_tree_factory
from dynamic_pyi_generator.data_type_tree.generic_type.dict_data_type_tree import (
    DictDataTypeTree,
    DictMetadata,
    DictMetadataComparison,
    KeyInfo,
)
from dynamic_pyi_generator.data_type_tree.generic_type.mapping_data_type_tree import MappingDataTypeTree
from dynamic_pyi_generator.file_modifiers.yaml_file_modifier import YamlFileModifier
from dynamic_pyi_generator.strategies import ParsingStrategies
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
    imports_to_check: Final = ("Mapping", "Any", "dict", "TypedDict", "MappingProxyType")
    """Imports that will be checked in case they were needed."""

    @pytest.mark.parametrize(
        "tree, expected_output, expected_n_childs",
        [
            (
                DictDataTypeTree(
                    {"name": "Joan"}, name=NAME, strategies=ParsingStrategies(min_height_to_define_type_alias=0)
                ),
                f"""class {NAME}(TypedDict):
{TAB}name: str""",
                1,
            ),
            (
                DictDataTypeTree(
                    {"age": 22}, name=NAME, strategies=ParsingStrategies(min_height_to_define_type_alias=0)
                ),
                f"""class {NAME}(TypedDict):
{TAB}age: int""",
                1,
            ),
            (
                DictDataTypeTree(
                    {"name": "Joan", "age": 21},
                    name=NAME,
                    strategies=ParsingStrategies(min_height_to_define_type_alias=0),
                ),
                f"""class {NAME}(TypedDict):
{TAB}name: str
{TAB}age: int""",
                2,
            ),
            (
                DictDataTypeTree(
                    {"name": "Joan", "kids": ["A", "B"]},
                    name=NAME,
                    strategies=ParsingStrategies(min_height_to_define_type_alias=0),
                ),
                f"""class {NAME}(TypedDict):
{TAB}name: str
{TAB}kids: {NAME}Kids""",
                2,
            ),
            (
                DictDataTypeTree(
                    {"name": "Joan", "kids": ["A", "B"], "parents": ["C", "D"]},
                    name=NAME,
                    strategies=ParsingStrategies(min_height_to_define_type_alias=0),
                ),
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
        Test the `get_str_top_node` method of the `DictDataTypeTree` class.

        Args:
            tree (TupleDataTypeTree): An instance of the `TupleDataTypeTree` class.
            expected_output (str): The expected output string.
            expected_n_childs (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[TupleDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        assert expected_n_childs == len(tree), "Not all childs were correctly parsed"
        assert expected_output == tree.get_str_top_node()
        assert_imports(tree, self.imports_to_check)

    @pytest.mark.parametrize(
        "tree, expected_output, expected_n_childs",
        [
            (
                DictDataTypeTree(
                    {"name and surname": "Joan B."},
                    name=NAME,
                    strategies=ParsingStrategies(min_height_to_define_type_alias=0),
                ),
                f"""{NAME} = TypedDict(
    "{NAME}",
    {{
        "name and surname": str,
    }},
)""",
                1,
            ),
            (
                DictDataTypeTree(
                    {"$": 22.0, "own_list": [1, 2, 3]},
                    name=NAME,
                    strategies=ParsingStrategies(min_height_to_define_type_alias=0),
                ),
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
                DictDataTypeTree(
                    {"$": 22, "my_list": [1, 2, 3], "my_list2": [2, 3]},
                    name=NAME,
                    strategies=ParsingStrategies(min_height_to_define_type_alias=0),
                ),
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
        Test the `get_str_top_node` method of the `DictDataTypeTree` class.

        Args:
            tree (TupleDataTypeTree): An instance of the `TupleDataTypeTree` class.
            expected_output (str): The expected output string.
            expected_n_childs (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[TupleDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        assert expected_n_childs == len(tree), "Not all childs were correctly parsed"
        assert expected_output == tree.get_str_top_node()
        assert_imports(tree, self.imports_to_check)


class TestGetStrHeight:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    imports_to_check: Final = ("Mapping", "Any", "dict", "TypedDict", "MappingProxyType")
    """Imports that will be checked in case they were needed."""

    @pytest.mark.parametrize(
        "tree, expected_output",
        [
            (
                DictDataTypeTree(
                    {"name": "Joan", "kids": ["A", "B"]},
                    name=NAME,
                    strategies=ParsingStrategies(min_height_to_define_type_alias=0),
                ),
                f"""class {NAME}(TypedDict):
{TAB}name: str
{TAB}kids: {NAME}Kids""",
            ),
            (
                DictDataTypeTree(
                    {"name": "Joan", "kids": ["A", "B"]},
                    name=NAME,
                    strategies=ParsingStrategies(min_height_to_define_type_alias=1),
                ),
                f"""class {NAME}(TypedDict):
{TAB}name: str
{TAB}kids: List[str]""",
            ),
        ],
    )
    def test_get_str_top_node_based_on_height(
        self,
        tree: DictDataTypeTree,
        expected_output: str,
    ) -> None:
        """
        Test the `get_str_top_node` method of the `DictDataTypeTree` class.

        Args:
            tree (TupleDataTypeTree): An instance of the `TupleDataTypeTree` class.
            expected_output (str): The expected output string.
            expected_n_childs (int): The expected number of child nodes in the tree.
            assert_imports (Callable[[TupleDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        assert expected_output == tree.get_str_top_node()

    @pytest.mark.parametrize(
        "data, min_height, expected_output",
        [
            ([2, {"name": "Joan", "kids": ["A", "B"]}], 0, f"{NAME} = List[Union[ExampleDict, int]]"),
            ([2, {"name": "Joan", "kids": ["A", "B"]}], 1, f"{NAME} = List[Union[ExampleDict, int]]"),
            ([2, {"name": "Joan", "kids": ["A", "B"]}], 2, f"{NAME} = List[Union[ExampleDict, int]]"),
        ],
    )
    def test_permissions(self, data: object, min_height: int, expected_output: str) -> None:
        error = "No matter the minimum height set up, `TypedDict` should always have preference"
        tree = data_type_tree_factory(
            data, name=self.NAME, strategies=ParsingStrategies(min_height_to_define_type_alias=min_height)
        )
        assert expected_output == tree.get_str_top_node(), error


class TestClassDocstringFromKey:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "tree, expected_output",
        [
            (
                DictDataTypeTree(
                    data={"name": "Joan", "doc": "This is a docstring"},
                    name=NAME,
                    strategies=ParsingStrategies(dict_strategy="TypedDict", key_used_as_doc="doc"),
                ),
                f'''class {NAME}(TypedDict):
{TAB}"""This is a docstring."""

{TAB}name: str
{TAB}doc: str''',
            ),
            (
                DictDataTypeTree(
                    data={"name": "Joan", "doc": "This is a docstring"},
                    name=NAME,
                    strategies=ParsingStrategies(dict_strategy="TypedDict", key_used_as_doc="doc2"),
                ),
                f"""class {NAME}(TypedDict):
{TAB}name: str
{TAB}doc: str""",
            ),
        ],
    )
    def test_docstring_is_created(self, tree: DictDataTypeTree, expected_output: str) -> None:
        assert expected_output == tree.get_str_top_node()

    @pytest.mark.parametrize(
        "tree, expected_last_line",
        [
            (
                DictDataTypeTree(
                    data={"full name": "Joan", "doc": "This is a docstring"},
                    name=NAME,
                    strategies=ParsingStrategies(dict_strategy="TypedDict", key_used_as_doc="doc"),
                ),
                '''"""This is a docstring."""''',
            ),
            (
                DictDataTypeTree(
                    data={"full name": "Joan", "doc": "This is a docstring"},
                    name=NAME,
                    strategies=ParsingStrategies(dict_strategy="TypedDict", key_used_as_doc="doc2"),
                ),
                "",
            ),
        ],
    )
    def test_docstring_is_created_in_functional_syntax(self, tree: DictDataTypeTree, expected_last_line: str) -> None:
        if expected_last_line:
            assert expected_last_line == tree.get_str_top_node().splitlines()[-1]
        else:
            assert '""""' not in tree.get_str_top_node().splitlines()[-1]


class TestDictMerge:
    PREFFIX: Final = YamlFileModifier.preffix

    @pytest.mark.parametrize(
        "data, expected_merged_data, expected_key_info",
        [
            (
                [
                    {"b": 2, f"{PREFFIX}b": "doc"},
                    {},
                ],
                {"b": 2, f"{PREFFIX}b": "doc"},
                {"b": KeyInfo(name="b", docstring="doc", required=False)},
            ),
            (
                [
                    {},
                    {"b": 2, f"{PREFFIX}b": "doc"},
                ],
                {"b": 2, f"{PREFFIX}b": "doc"},
                {"b": KeyInfo(name="b", docstring="doc", required=False)},
            ),
            (
                [
                    {"b": 4},
                    {"b": 2},
                ],
                {"b": 2},
                {"b": KeyInfo(name="b", required=True)},
            ),
            (
                [
                    {"b": 4},
                    {"a": 2},
                ],
                {"b": 4, "a": 2},
                {
                    "b": KeyInfo(name="b", required=False),
                    "a": KeyInfo(name="a", required=False),
                },
            ),
            (
                [
                    {"b": 4},
                    {"a": 2, "b": 7, f"{PREFFIX}b": "doc"},
                ],
                {"b": 7, "a": 2, f"{PREFFIX}b": "doc"},
                {
                    "b": KeyInfo(name="b", docstring="doc", required=True),
                    "a": KeyInfo(name="a", required=False),
                },
            ),
            (
                [
                    {"a": 2, "b": 7, f"{PREFFIX}b": "doc"},
                    {"b": 4},
                ],
                {"b": 4, "a": 2, f"{PREFFIX}b": "doc"},
                {
                    "b": KeyInfo(name="b", docstring="doc", required=True),
                    "a": KeyInfo(name="a", required=False),
                },
            ),
        ],
    )
    def test_from_multiple_dict_data_type_trees(
        self,
        data: Sequence[Mapping[Hashable, object]],
        expected_merged_data: DictDataTypeTree,
        expected_key_info: Mapping[Hashable, KeyInfo],
    ) -> None:
        inputs = [
            DictDataTypeTree(dct, name="Name", strategies=ParsingStrategies(dict_strategy="TypedDict")) for dct in data
        ]
        merged_tree = DictDataTypeTree.from_multiple_dict_data_type_trees(*inputs)
        assert expected_merged_data == merged_tree.data
        assert expected_key_info == merged_tree.dict_metadata.key_info


class TestSimilarityMerge:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "data, expected_merge, expected_str_all_nodes",
        [
            (
                [{"name": "a", "age": 22}, {"name": "b", "age": 23, "optional_field": 27}],
                True,
                (
                    f"""class ExampleDict(TypedDict):
{TAB}name: str
{TAB}age: int
{TAB}optional_field: NotRequired[int]""",
                    "Example = List[ExampleDict]",
                ),
            ),
            (
                [{"a": "a", "b": 22}, {"c": "b", "d": 23}],
                False,
                (
                    f"""class ExampleDict2(TypedDict):
{TAB}c: str
{TAB}d: int""",
                    f"""class ExampleDict(TypedDict):
{TAB}a: str
{TAB}b: int""",
                    "Example = List[Union[ExampleDict, ExampleDict2]]",
                ),
            ),
        ],
    )
    def test_list_containing_dictionaries(
        self, data: Sized, expected_merge: bool, expected_str_all_nodes: Tuple[str, ...]
    ) -> None:
        tree = data_type_tree_factory(
            data, name=self.NAME, strategies=ParsingStrategies(min_height_to_define_type_alias=1)
        )

        if not expected_merge:
            assert len(tree) == len(data)
        assert sorted(expected_str_all_nodes) == sorted(tree.get_strs_all_nodes_unformatted(include_imports=False))

    @pytest.mark.parametrize(
        "data, expected_merge, expected_str_all_nodes",
        [
            (
                ({"name": "a", "age": 22}, {"name": "b", "age": 23, "optional_field": 27}),
                True,
                (
                    f"""class ExampleDict(TypedDict):
{TAB}name: str
{TAB}age: int
{TAB}optional_field: NotRequired[int]""",
                    "Example = Tuple[ExampleDict, ExampleDict]",
                ),
            ),
            (
                ({"a": "a", "b": 22}, {"c": "b", "d": 23}),
                False,
                (
                    f"""class ExampleDict(TypedDict):
{TAB}a: str
{TAB}b: int""",
                    f"""class ExampleDict2(TypedDict):
{TAB}c: str
{TAB}d: int""",
                    "Example = Tuple[ExampleDict, ExampleDict2]",
                ),
            ),
        ],
    )
    def test_tuple_containing_dictionaries(
        self, data: Sized, expected_merge: bool, expected_str_all_nodes: Tuple[str, ...]
    ) -> None:
        tree = data_type_tree_factory(data, name=self.NAME, strategies=ParsingStrategies(tuple_size_strategy="fixed"))

        if not expected_merge:
            assert len(tree) == len(data)
        assert expected_str_all_nodes == tree.get_strs_all_nodes_unformatted(include_imports=False)


class TestKeyDocstring:
    NAME: Final = "Example"
    PREFFIX: Final = YamlFileModifier.preffix

    @pytest.mark.parametrize(
        "tree, expected_output",
        [
            (
                DictDataTypeTree(
                    data={"name": "Joan", "age": 22, f"{PREFFIX}name": "This is name doc"},
                    name=NAME,
                    strategies=ParsingStrategies(dict_strategy="TypedDict", key_used_as_doc="doc"),
                ),
                f'''class {NAME}(TypedDict):
{TAB}name: str
{TAB}"""This is name doc."""
{TAB}age: int''',
            ),
            (
                DictDataTypeTree(
                    data={"name": "Joan", "age": 22, f"{PREFFIX}age": "This is age doc"},
                    name=NAME,
                    strategies=ParsingStrategies(dict_strategy="TypedDict", key_used_as_doc="doc"),
                ),
                f'''class {NAME}(TypedDict):
{TAB}name: str
{TAB}age: int
{TAB}"""This is age doc."""''',
            ),
            (
                DictDataTypeTree(
                    data={
                        "name": "Joan",
                        "age": 22,
                        f"{PREFFIX}age": "This is age doc",
                        f"{PREFFIX}name": "This is name doc",
                    },
                    name=NAME,
                    strategies=ParsingStrategies(dict_strategy="TypedDict", key_used_as_doc="doc"),
                ),
                f'''class {NAME}(TypedDict):
{TAB}name: str
{TAB}"""This is name doc."""
{TAB}age: int
{TAB}"""This is age doc."""''',
            ),
        ],
    )
    def test_key_docstring_is_created(self, tree: DictDataTypeTree, expected_output: str) -> None:
        assert expected_output == tree.get_str_top_node()

    def test_key_docstring_is_not_created_in_functional_syntax(self) -> None:
        key_docstring = "This is a key doc"
        tree = DictDataTypeTree(
            data={"full name": "Joan", "doc": "This is a docstring", f"{self.PREFFIX}full name": key_docstring},
            name=self.NAME,
            strategies=ParsingStrategies(dict_strategy="TypedDict", key_used_as_doc="doc"),
        )
        assert key_docstring not in tree.get_str_top_node().splitlines()

    @pytest.mark.parametrize(
        "data1, data2, expected_same_hash",
        [
            ({"name": "Joan", f"{PREFFIX}name": "This is a doc"}, {"name": "Joan"}, True),
            ({"age": 22, f"{PREFFIX}age": "This is a doc"}, {"age": 23}, True),
            ({"age": 22, f"{PREFFIX}age": "This is a doc"}, {"age": "22"}, False),
        ],
    )
    def test_hidden_key_docs_do_not_change_hash(
        self, data1: Dict[Any, Any], data2: Dict[Any, Any], expected_same_hash: bool
    ) -> None:
        tree1 = DictDataTypeTree(data1, name="Tree1")
        tree2 = DictDataTypeTree(data2, name="Tree2")
        assert expected_same_hash == (hash(tree1) == hash(tree2))

    @pytest.mark.parametrize(
        "data, should_be_functional_syntax",
        [
            ({"a": 2}, False),
            ({"a": 2, ".b": 2}, True),
            ({"a": 2, " b": 2}, True),
            ({"a": 2, "from": 2}, True),
            ({"a": 2, "in": 2}, True),
            ({"a": 2, "class": 2}, True),
        ],
    )
    def test_typed_dict_goes_to_functional_syntax(
        self, data: Mapping[Hashable, object], should_be_functional_syntax: bool
    ) -> None:
        tree = DictDataTypeTree(data, name="Example", strategies=ParsingStrategies(dict_strategy="TypedDict"))
        assert should_be_functional_syntax == tree.dict_metadata.is_functional_syntax


class TestOriginalDataNotMutated:
    @pytest.mark.parametrize(
        "input_data",
        [
            [{"name": "Manu"}, {"name": "Joan", "age": 22}],
            [{"name": "Manu"}, {}],
        ],
    )
    def test_mutation(self, input_data: List[Dict[Hashable, object]]) -> None:
        input_data_before = deepcopy(input_data)
        data_type_tree_factory(
            input_data, strategies=ParsingStrategies(merge_different_typed_dicts_if_similarity_above=1), name="Example"
        )
        assert input_data_before == input_data


class TestDictMetadata:
    PREFFIX: Final = YamlFileModifier.preffix

    @pytest.mark.parametrize(
        "data, expected_output",
        [
            ({"a": 2, "b": 1}, True),
            ({1: 2, "b": 1}, False),
            ({"a": 2, "b": "a"}, True),
            ({"a": "a", "b": "a"}, True),
        ],
    )
    def test_all_keys_are_string(self, data: Mapping[Hashable, object], expected_output: bool) -> None:
        assert expected_output == DictMetadata._all_keys_are_string(data)

    @pytest.mark.parametrize(
        "data, expected_output",
        [
            ({"a": 2, "b": 1}, True),
            ({":a": 2, "b": 1}, False),
            ({" a": 2, "b": 1}, False),
            ({".a": 2, "b": 1}, False),
            ({".a.": 2, "b": 1}, False),
            ({"1a": 2, "b": 1}, False),
            ({"a1": 2, "b": 1}, True),
        ],
    )
    def test_all_keys_are_parsable(self, data: Mapping[Hashable, object], expected_output: bool) -> None:
        assert (
            expected_output
            == DictMetadata(
                data, hidden_key_preffix="", strategies=ParsingStrategies(dict_strategy="TypedDict")
            )._all_keys_are_parsable()
        )

    @pytest.mark.parametrize(
        "data, expected_output",
        [
            ({"b": 2, f"{PREFFIX}b": "doc"}, {"b": "doc"}),
            ({"b": 2, f"{PREFFIX}b": "doc", "a": 1}, {"b": "doc"}),
            ({".b": 2, f"{PREFFIX}b": "doc", "a": 1}, {}),
        ],
    )
    def test_get_key_docstrings(self, data: Mapping[Hashable, object], expected_output: Mapping[str, object]) -> None:
        assert (
            expected_output
            == DictMetadata(
                data, hidden_key_preffix=self.PREFFIX, strategies=ParsingStrategies(dict_strategy="TypedDict")
            ).get_key_docstrings()
        )

    @pytest.mark.parametrize(
        "initial_dict, other_dict, expected_dict, expected_key_info",
        [
            (
                {"a": 2},
                {"a": 3},
                {"a": 2},
                {"a": KeyInfo(name="a", docstring="", required=True)},
            ),
            (
                {"a": 2, "b": 2},
                {"a": 3},
                {"a": 2, "b": 2},
                {
                    "a": KeyInfo(name="a", docstring="", required=True),
                    "b": KeyInfo(name="b", docstring="", required=False),
                },
            ),
            (
                {"a": 3},
                {"a": 2, "b": 2},
                {"a": 3, "b": 2},
                {
                    "a": KeyInfo(name="a", docstring="", required=True),
                    "b": KeyInfo(name="b", docstring="", required=False),
                },
            ),
            (
                {"a": 3, f"{PREFFIX}a": "a_doc"},
                {"a": 2, "b": 2},
                {"a": 3, f"{PREFFIX}a": "a_doc", "b": 2},
                {
                    "a": KeyInfo(name="a", docstring="a_doc", required=True),
                    "b": KeyInfo(name="b", docstring="", required=False),
                },
            ),
            (
                {"a": 2, "b": 2},
                {"a": 3, f"{PREFFIX}a": "a_doc"},
                {"a": 2, f"{PREFFIX}a": "a_doc", "b": 2},
                {
                    "a": KeyInfo(name="a", docstring="a_doc", required=True),
                    "b": KeyInfo(name="b", docstring="", required=False),
                },
            ),
            (
                {"a": 3, f"{PREFFIX}a": "a_doc"},
                {"a": 3, f"{PREFFIX}a": "a_doc2"},
                {"a": 3, f"{PREFFIX}a": "a_doc"},
                {
                    "a": KeyInfo(name="a", docstring="a_doc", required=True),
                },
            ),
            (
                {"a": 3, f"{PREFFIX}a": "a_doc2"},
                {"a": 3, f"{PREFFIX}a": "a_doc"},
                {"a": 3, f"{PREFFIX}a": "a_doc2"},
                {
                    "a": KeyInfo(name="a", docstring="a_doc2", required=True),
                },
            ),
            (
                {".a": 3, f"{PREFFIX}.a": "a_doc2"},
                {".a": 3, f"{PREFFIX}.a": "a_doc"},
                {".a": 3, f"{PREFFIX}.a": "a_doc2"},
                {
                    ".a": KeyInfo(name=".a", docstring="a_doc2", required=True),
                },
            ),
        ],
    )
    def test_update(
        self,
        initial_dict: Mapping[Hashable, object],
        other_dict: Mapping[Hashable, object],
        expected_dict: Mapping[Hashable, object],
        expected_key_info: Mapping[Hashable, KeyInfo],
    ) -> None:
        strategies = ParsingStrategies(dict_strategy="TypedDict")
        metadata = DictMetadata(initial_dict, hidden_key_preffix=self.PREFFIX, strategies=strategies)
        metadata.update(DictMetadata(other_dict, hidden_key_preffix=self.PREFFIX, strategies=strategies))
        assert expected_dict == metadata._data
        assert expected_key_info == metadata.key_info

    @pytest.mark.parametrize(
        "data, include_hidden_keys, expected_output",
        [
            ({"b": 2, f"{PREFFIX}b": "doc"}, False, {"b"}),
            ({"b": 2, "a": "doc"}, False, {"b", "a"}),
            ({"b": 2, f"{PREFFIX}b": "doc"}, True, {f"{PREFFIX}b", "b"}),
            ({"b": 2, "a": "doc"}, True, {"b", "a"}),
            ({1: 2, "a": "doc"}, True, {1, "a"}),
            ({1: 2, f"{PREFFIX}a": "doc", "a": 2}, True, {1, "a", f"{PREFFIX}a"}),
        ],
    )
    def test_get_keys(
        self, data: Mapping[Hashable, object], expected_output: Set[str], include_hidden_keys: bool
    ) -> None:
        assert expected_output == DictMetadata(
            data, hidden_key_preffix=self.PREFFIX, strategies=ParsingStrategies(dict_strategy="TypedDict")
        ).get_keys(include_hidden_prefix_keys=include_hidden_keys)

    @pytest.mark.parametrize(
        "dicts, expected_output, expected_similarity",
        [
            (
                [{"a": 2}, {"a": 3}, {"a": 2}],
                DictMetadataComparison(common_keys={"a"}, value_types={"a": {int}}),
                100,
            ),
            (
                [{"a": 2}, {"b": 3}, {"c": 2}],
                DictMetadataComparison(
                    non_common_keys={"a", "b", "c"}, value_types={"a": {int}, "b": {int}, "c": {int}}
                ),
                0,
            ),
            (
                [{"a": 2}, {"a": 3.2}, {"b": 2}],
                DictMetadataComparison(non_common_keys={"a", "b"}, value_types={"a": {float}, "b": {int}}),
                0,
            ),
            (
                [{"a": 2, "b": 3}, {"a": 3}, {"a": "b", "j": "a"}],
                DictMetadataComparison(
                    common_keys={"a"},
                    non_common_keys={"b", "j"},
                    value_types={"a": {int, str}, "b": {int}, "j": {str}},
                ),
                33,
            ),
            (
                [{}, {"a": 3}, {}],
                DictMetadataComparison(non_common_keys={"a"}, value_types={"a": {int}}),
                0,
            ),
        ],
    )
    def test_get_info_from_multiple_dicts(
        self,
        dicts: Sequence[Mapping[Hashable, object]],
        expected_output: DictMetadataComparison,
        expected_similarity: int,
    ) -> None:
        dicts_ = [
            DictMetadata(dct, hidden_key_preffix=self.PREFFIX, strategies=ParsingStrategies(dict_strategy="TypedDict"))
            for dct in dicts
        ]
        comparison = DictMetadata.compare_multiple_dicts(*dicts_)
        assert expected_output == comparison
        assert expected_similarity == comparison.percentage_similarity
