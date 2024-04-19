import itertools
import subprocess
import timeit
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Literal,
    Set,
    Tuple,
)

import pandas as pd
import pytest

from lazy_type_hint.data_type_tree import DataTypeTree, data_type_tree_factory
from lazy_type_hint.strategies import ParsingStrategies
from lazy_type_hint.utils import TAB, check_if_command_available


@dataclass(frozen=True)
class StrategiesTesting(ParsingStrategies):
    @classmethod
    def generate_all(cls) -> Iterable[ParsingStrategies]:
        # Must be defined with all input arguments and in otder
        input_dict = {
            "list_strategy": ["Sequence", "list"],
            "tuple_size_strategy": ["fixed", "any size"],
            "dict_strategy": ["TypedDict", "Mapping", "dict"],
            "pandas_strategies": ["Full type hint", "Type hint only for autocomplete", "Do not type hint columns"],
            "min_height_to_define_type_alias": [2],
            "key_used_as_doc": [""],
            "merge_different_typed_dicts_if_similarity_above": [20, 80],
            "typed_dict_read_only_values": [True, False],
            "check_max_n_type_elements_within_container": [1, 100],
        }
        # Generate all combinations of values
        for combination in itertools.product(*input_dict.values()):  # type: ignore
            yield cls(*combination)


@pytest.mark.parametrize("strategies", StrategiesTesting.generate_all())
@pytest.mark.parametrize("to_check", ("imports", "strategies"))
def test_all_children_share(create_sample: Callable[[str], str], strategies: ParsingStrategies, to_check: str) -> None:
    data = create_sample("dictionary")
    tree = data_type_tree_factory(data, strategies=strategies, name="Example")

    parent_object = getattr(tree, to_check)

    def check_objects_are_shared(tree: DataTypeTree) -> None:
        for child in tree:
            assert id(parent_object) == id(getattr(child, to_check)), f"Not all children are sharing same {to_check}"
            check_objects_are_shared(child)

    check_objects_are_shared(tree)


class TestIntegration:
    @pytest.mark.integration
    @pytest.mark.skipif(
        not check_if_command_available("python"), reason="Python must be available within the terminal."
    )
    @pytest.mark.parametrize("strategies", StrategiesTesting.generate_all())
    @pytest.mark.parametrize("data_type", ["frozenset", "set", "list", "tuple", "dictionary", "mapping"])
    def test_integration(
        self, strategies: ParsingStrategies, create_sample: Callable[[str], str], data_type: str, tmp_path: str
    ) -> None:
        data = create_sample(data_type)
        data_before = str(data)
        string = data_type_tree_factory(data, name="Example", strategies=strategies).get_str_all_nodes(
            include_imports=True
        )

        self.assert_no_unused_classes(string)
        self.assert_no_redefined_classes(string)
        self.assert_no_double_whitespace(string)
        self.assert_basic_format(string)
        self.assert_no_broken_string_representation(string, tmp_path=tmp_path)
        self.assert_python_38_compatible(string)
        self.assert_input_object_is_not_modified(data_before, str(data))

    @staticmethod
    def assert_input_object_is_not_modified(data_before: str, data_after: str) -> None:
        assert data_before == data_after

    @staticmethod
    def assert_python_38_compatible(string: str) -> None:
        """
        Asserts that the given string is compatible with Python 3.8.

        Args:
            string (str): The string to check for compatibility.
        """
        to_check = ["dict", "list", "set", "tuple"]
        for line in string.splitlines():
            assert all(f"{check}[" not in line for check in to_check)

    @staticmethod
    def assert_no_broken_string_representation(string: str, tmp_path: str) -> None:
        """Compile and call corresponding string representation.

        Not done via `exec()` as this one was presenting an inconsistent behaviour.
        """
        file = "tmp.py"
        full_path_file = Path(tmp_path) / file
        full_path_file.write_text(data=string)
        result = subprocess.run(f"python3 -m poetry run {full_path_file}", capture_output=True, text=True)

        assert not result.stdout
        assert not result.stderr

    def assert_no_unused_classes(self, string: str) -> None:
        types_defined: Set[str] = set()
        for line in string.splitlines():
            for type_defined in types_defined.copy():
                if type_defined in line:
                    idx = line.find(type_defined) + len(type_defined)
                    if idx >= len(line) or idx < len(line) and not line[idx].isalpha():
                        types_defined.remove(type_defined)
            name = self._get_name_type_alias(line)
            if name:
                types_defined.add(name)
        error = (
            "Only the new class created can be the only non-used class. However, more than 1 unused class/type alias "
            f"was detected: {', '.join(types_defined)}"
        )
        assert len(types_defined) == 1 or len(types_defined) == 0, error

    def assert_no_redefined_classes(self, string: str) -> None:
        all_types_defined: Set[str] = set()
        for line in string.splitlines():
            name = self._get_name_type_alias(line)
            if name:
                if name in all_types_defined:
                    pytest.fail(f"A class/type alias was detected to be redefined: {name}")
                all_types_defined.add(name)

    def assert_no_double_whitespace(self, string: str) -> None:
        for idx, line in enumerate(string.splitlines()):
            if TAB not in line and "  " in line:
                pytest.fail(f"Double whitespaces were detected in line {idx}: {line}")

    def assert_basic_format(self, string: str) -> None:
        strings = string.splitlines()
        for idx, line in enumerate(strings):
            if line.startswith("class"):
                error = "There has to be exaxctly two empty lines before defining a class."
                assert strings[idx - 1] == "", error
                assert strings[idx - 2] == "", error
                assert strings[idx - 3] != "", error

    @staticmethod
    def _get_name_type_alias(line: str) -> str:
        if "=" in line:
            return line.split("=")[0].strip().rstrip()
        if "(TypedDict)" in line:
            return line.split("(TypedDict)")[0].split(" ")[-1].strip().rstrip()
        return ""


class TestRename:
    def test(self) -> None:
        tree = data_type_tree_factory([1, 2, 3, [1, 2, 3]], name="Example")
        self.assert_names("Example", tree)
        tree.rename("Example2")
        self.assert_names("Example2", tree)

    @staticmethod
    def assert_names(name: str, tree: DataTypeTree) -> None:
        assert f"{name}Int" == tree.children[0].name  # type: ignore
        assert f"{name}List" == tree.children[1].name  # type: ignore
        assert f"{name}ListInt" == tree.children[1].children[0].name  # type: ignore


class TestHash:
    # fmt: off
    @pytest.mark.parametrize(
        "data1, data2, strategies, should_be_equal",
        [
            ([1, 2, 3], [4, 5, 6], ParsingStrategies(), True),
            ([1, "str", 3], [4, 5, 6], ParsingStrategies(), False),
            ([1, "str", 3], ["a", 5, 6], ParsingStrategies(), True),
            ([1, {1,2}, 3], [{4,5}, 5, 6], ParsingStrategies(), True),
            ([1, {1,2}, 3], [{4,"a"}, 5, 6], ParsingStrategies(), False),
            ([1, "str", (1, 2)], ["a", 5, (1,)], ParsingStrategies(), False),
            ([1, "str", (1, 2)], ["a", 5, (1,)], ParsingStrategies(tuple_size_strategy="any size"), True),
            ([1, "str", (1, "b")], ["a", 5, (1,)], ParsingStrategies(), False),
            ([1, "str", (1, "b")], ["a", 5, ("c", 1,)], ParsingStrategies(), False),
            ([1, "str", (1, "b")], ["a", 5, ("c", 1,)], ParsingStrategies(tuple_size_strategy="any size"), True),
            ([1, "str", (1, {1,2})], ["a", 5, (1,)], ParsingStrategies(), False),
            # Dicts
            ({"name": "Patrick"}, {"age": "22"}, ParsingStrategies(dict_strategy="dict"), True),
            ({"name": "Patrick"}, {"age": 22}, ParsingStrategies(dict_strategy="dict"), False),
            ({22: 21}, {"age2": 22}, ParsingStrategies(dict_strategy="dict"), False),
            ({22: 21}, {"age2": "name"}, ParsingStrategies(dict_strategy="dict"), False),
            ({22: 21}, {"age2": 22, "age3": "name"}, ParsingStrategies(dict_strategy="dict"), False),
            ({22: 21}, {"age2": 22, "age3": 21}, ParsingStrategies(dict_strategy="dict"), False),
            ({"age1": 21}, {"age2": 22, "age3": 21}, ParsingStrategies(dict_strategy="dict"), True),
            ({"age1": 21, "age4": 16}, {"age2": 22, "age3": 21}, ParsingStrategies(dict_strategy="dict"), True),
            ({"age1": 21, 37: 16}, {"age2": 22, 22: 21}, ParsingStrategies(dict_strategy="TypedDict"), True),
            # TypedDict
            ({"age1": 21, "age2": 16}, {"age2": 22, "age3": 21}, ParsingStrategies(dict_strategy="TypedDict"), False),
            ({"age1": 21, "age2": 16}, {"age1": 22, "age2": 21}, ParsingStrategies(dict_strategy="TypedDict"), True),
            ({"age1": 21, "age2": 16}, {"age1": 22, "age2": "a"}, ParsingStrategies(dict_strategy="TypedDict"), False),
            # Functions
            ({lambda x: print("Hi")}, {lambda y: None}, ParsingStrategies(), True),  # noqa: ARG005
            ({lambda x: print("Hi")}, {lambda y: None, lambda x: None}, ParsingStrategies(), True),  # noqa: ARG005
            # Pandas DataFrame
            ([pd.DataFrame({"A": [1]})], [pd.DataFrame({"A": [2]})], ParsingStrategies(), True),
            ([pd.DataFrame({"A": [1]})], [pd.DataFrame({"B": [2]})], ParsingStrategies(), False),
            ([pd.DataFrame({("A",): [1]})], [pd.DataFrame({("A", "B"): [2]})], ParsingStrategies(), False),
        ],
    )
    # fmt: on
    def test_hash(self, data1: object, data2: object, should_be_equal: bool, strategies: ParsingStrategies) -> None:
        tree1 = data_type_tree_factory(data1, name="Name1", strategies=strategies)
        tree2 = data_type_tree_factory(data2, name="Name2", strategies=strategies)

        assert should_be_equal == (tree1._get_hash() == tree2._get_hash())
        assert should_be_equal == (hash(tree1) == hash(tree2))


@pytest.mark.usefixtures("_serial")
class TestCheckNMaxElementsFeature:
    @pytest.mark.parametrize("type_", [set, frozenset, list, tuple])
    def test_sequence_and_set(self, type_: Any) -> None:
        iterable = type_(list(range(1_000_000)))
        n = 10  # Number of executions
        total_time = timeit.timeit(
            lambda: data_type_tree_factory(
                iterable, name="Example", strategies=ParsingStrategies(check_max_n_elements_within_container=100)
            ),
            number=n,
        )

        average_time = total_time / n
        total_time = timeit.timeit(
            lambda: data_type_tree_factory(
                iterable, name="Example", strategies=ParsingStrategies(check_max_n_elements_within_container=200)
            ),
            number=n,
        )

        assert average_time * 1.5 < (
            total_time / n
        ), "It seems changing the strategy to check more elements does not affect the performance"

    @pytest.mark.parametrize("strategy", ["dict", "Mapping"])
    @pytest.mark.parametrize("type_", [dict, MappingProxyType])
    def test_mapping(self, strategy: Literal["dict", "Mapping"], type_: Any) -> None:
        n_elements = 1_000_000
        dct = type_(dict(zip(range(n_elements), range(n_elements))))
        n = 10  # Number of executions
        total_time = timeit.timeit(
            lambda: data_type_tree_factory(
                dct,
                name="Example",
                strategies=ParsingStrategies(dict_strategy=strategy, check_max_n_elements_within_container=100),
            ),
            number=n,
        )

        average_time = total_time / n
        total_time = timeit.timeit(
            lambda: data_type_tree_factory(
                dct,
                name="Example",
                strategies=ParsingStrategies(dict_strategy=strategy, check_max_n_elements_within_container=200),
            ),
            number=n,
        )

        assert average_time * 1.5 < (
            total_time / n
        ), "It seems changing the strategy to check more elements does not affect the performance"


class TestCachedHash:
    def test(self, generate_tree_based_list: Callable[[int, int], List[Any]]) -> None:
        lst = generate_tree_based_list(depth=10, n_elements=3)  # type: ignore
        tree = data_type_tree_factory(lst, name="Example")

        time_before_cache = timeit.timeit(lambda: hash(tree), number=1)
        time_after_cache = timeit.timeit(lambda: hash(tree), number=1)

        assert time_after_cache < time_before_cache / 1_000


class TestRenameDeclaration:
    @pytest.mark.parametrize(
        "declaration, new_name, expected_output",
        [
            ("MyList = List[str]", "New", ("New = List[str]", "MyList")),
            ("MyDict = Dict[str, Any]", "New", ("New = Dict[str, Any]", "MyDict")),
            (f"class MyClass(Protocol):\n{TAB}...", "New", (f"class New(Protocol):\n{TAB}...", "MyClass")),
            (f"class MyClass():\n{TAB}...", "New", (f"class New():\n{TAB}...", "MyClass")),
            (f"class MyClass:\n{TAB}...", "New", (f"class New:\n{TAB}...", "MyClass")),
        ],
    )
    def test(self, declaration: str, new_name: str, expected_output: Tuple[str, str]) -> None:
        assert expected_output == DataTypeTree.rename_declaration(declaration, new_name=new_name)
