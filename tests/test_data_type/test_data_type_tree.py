import itertools
import subprocess
from collections import defaultdict
from dataclasses import dataclass, fields
from pathlib import Path
from typing import (
    Callable,
    Final,
    Iterable,
    List,
    Mapping,
    Set,
    Tuple,
    get_args,
    get_type_hints,
)

import pytest

from dynamic_pyi_generator.data_type_tree import DataTypeTree
from dynamic_pyi_generator.strategies import Strategies
from dynamic_pyi_generator.utils import TAB, check_if_command_available


@dataclass(frozen=True)
class StrategiesTesting(Strategies):
    @classmethod
    def generate_all(cls) -> Iterable[Strategies]:
        type_hints = get_type_hints(cls)
        input_dict: Mapping[str, List[str]] = defaultdict(list)
        for field in fields(cls):
            for arg in get_args(type_hints[field.name]):
                input_dict[field.name].append(arg)

        # Generate all combinations of values
        for combination in itertools.product(*input_dict.values()):
            yield cls(*combination)


@pytest.mark.parametrize("strategies", StrategiesTesting.generate_all())
@pytest.mark.parametrize("to_check", ("imports", "strategies"))
def test_all_childs_share(create_sample: Callable[[str], str], strategies: Strategies, to_check: str) -> None:
    data = create_sample("dictionary")
    cls = DataTypeTree.get_data_type_tree_for_type(type(data))
    tree = cls(data, strategies=strategies, name="Example")

    parent_object = getattr(tree, to_check)

    def check_objects_are_shared(tree: DataTypeTree) -> None:
        for child in tree:
            assert id(parent_object) == id(getattr(child, to_check)), f"Not all childs are sharing same {to_check}"
            check_objects_are_shared(child)

    check_objects_are_shared(tree)


class TestIntegration:
    test_files: Final = ("dictionary.py", "list.py", "set.py")
    test_files_dir: Final = Path(__file__).parent / "test_files"

    @pytest.mark.skipif(
        not check_if_command_available("python"), reason="Python must be available within the terminal."
    )
    @pytest.mark.parametrize("strategies", StrategiesTesting.generate_all())
    @pytest.mark.parametrize("data_type", ["frozenset", "set", "list", "tuple", "dictionary", "mapping"])
    def test_integration(
        self, strategies: Strategies, create_sample: Callable[[str], str], data_type: str, tmp_path: str
    ) -> None:
        data = create_sample(data_type)
        cls = DataTypeTree.get_data_type_tree_for_type(type(data))
        strings = cls(data, name="Example", strategies=strategies).get_strs_recursive_py(include_imports=True)

        self.assert_no_unused_classes(strings)
        self.assert_no_redefined_classes(strings)
        self.assert_no_double_whitespace(strings)

        self.assert_no_broken_string_representation(strings, tmp_path=tmp_path)

    @staticmethod
    def assert_no_broken_string_representation(strings: Tuple[str, ...], tmp_path: str) -> None:
        """Compile and call corresponding string representation.

        Not done via `exec()` as this one was presenting an inconsistent behaviour.
        """
        file = "tmp.py"
        full_path_file = Path(tmp_path) / file
        full_path_file.write_text(data="\n".join(strings))
        result = subprocess.run(f"python {full_path_file}", capture_output=True, text=True)

        assert not result.stdout
        assert not result.stderr

    def assert_no_unused_classes(self, strings: Tuple[str, ...]) -> None:
        types_defined: Set[str] = set()
        for line in strings:
            for type_defined in types_defined.copy():
                if type_defined in line:
                    types_defined.remove(type_defined)
            name = self._get_name_type_alias(line)
            if name:
                types_defined.add(name)
        assert len(types_defined) == 1, f"Some classes were created but they are not in use: {', '.join(types_defined)}"

    def assert_no_redefined_classes(self, strings: Tuple[str, ...]) -> None:
        all_types_defined: Set[str] = set()
        for line in strings:
            name = self._get_name_type_alias(line)
            if name:
                if name in all_types_defined:
                    pytest.fail(f"A class/type alias was detected to be redefined: {name}")
                all_types_defined.add(name)

    def assert_no_double_whitespace(self, strings: Tuple[str, ...]) -> None:
        for idx, line in enumerate(strings):
            if TAB not in line and "  " in line:
                pytest.fail(f"Double whitespaces were detected in line {idx}: {line}")

    @staticmethod
    def _get_name_type_alias(line: str) -> str:
        if "=" in line:
            return line.split("=")[0].strip().rstrip()
        if "(TypedDict)" in line:
            return line.split("(TypedDict)")[0].split(" ")[-1].strip().rstrip()
        return ""


class TestHash:
    # fmt: off
    @pytest.mark.parametrize(
        "data1, data2, strategies, should_be_equal",
        [
            ([1, 2, 3], [4, 5, 6], Strategies(), True),
            ([1, "str", 3], [4, 5, 6], Strategies(), False),
            ([1, "str", 3], ["a", 5, 6], Strategies(), True),
            ([1, {1,2}, 3], [{4,5}, 5, 6], Strategies(), True),
            ([1, {1,2}, 3], [{4,"a"}, 5, 6], Strategies(), False),
            ([1, "str", (1, 2)], ["a", 5, (1,)], Strategies(), False),
            ([1, "str", (1, 2)], ["a", 5, (1,)], Strategies(tuple_size_strategy="..."), True),
            ([1, "str", (1, "b")], ["a", 5, (1,)], Strategies(), False),
            ([1, "str", (1, "b")], ["a", 5, ("c", 1,)], Strategies(), False),
            ([1, "str", (1, "b")], ["a", 5, ("c", 1,)], Strategies(tuple_size_strategy="..."), True),
            ([1, "str", (1, {1,2})], ["a", 5, (1,)], Strategies(), False),
            # Dicts
            ({"name": "Patrick"}, {"age": "22"}, Strategies(dict_strategy="Dict"), True),
            ({"name": "Patrick"}, {"age": 22}, Strategies(dict_strategy="Dict"), False),
            ({22: 21}, {"age2": 22}, Strategies(dict_strategy="Dict"), False),
            ({22: 21}, {"age2": "name"}, Strategies(dict_strategy="Dict"), False),
            ({22: 21}, {"age2": 22, "age3": "name"}, Strategies(dict_strategy="Dict"), False),
            ({22: 21}, {"age2": 22, "age3": 21}, Strategies(dict_strategy="Dict"), False),
            ({"age1": 21}, {"age2": 22, "age3": 21}, Strategies(dict_strategy="Dict"), True),
            ({"age1": 21, "age4": 16}, {"age2": 22, "age3": 21}, Strategies(dict_strategy="Dict"), True),
            ({"age1": 21, 37: 16}, {"age2": 22, 22: 21}, Strategies(dict_strategy="TypedDict"), True),
            # TypedDict
            ({"age1": 21, "age2": 16}, {"age2": 22, "age3": 21}, Strategies(dict_strategy="TypedDict"), False),
            ({"age1": 21, "age2": 16}, {"age1": 22, "age2": 21}, Strategies(dict_strategy="TypedDict"), True),
            ({"age1": 21, "age2": 16}, {"age1": 22, "age2": "a"}, Strategies(dict_strategy="TypedDict"), False),
        ],
    )
    # fmt: on
    def test_hash(self, data1: object, data2: object, should_be_equal: bool, strategies: Strategies) -> None:
        tree1 = DataTypeTree.get_data_type_tree_for_type(type(data1))(data1, name="Name1", strategies=strategies)
        tree2 = DataTypeTree.get_data_type_tree_for_type(type(data2))(data2, name="Name2", strategies=strategies)

        assert should_be_equal == (tree1._get_hash() == tree2._get_hash())
        assert should_be_equal == (hash(tree1) == hash(tree2))
