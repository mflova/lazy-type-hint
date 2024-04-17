import random
import timeit
from pathlib import Path
from typing import Any, Final, List, Literal

import pytest
import yaml

from lazy_type_hint.data_type_tree import data_type_tree_factory
from lazy_type_hint.strategies import ParsingStrategies


def generate_tree_based_list(depth: int, n_elements: int) -> List[Any]:
    def append_elem(lst: List[Any], depth: int, n_elements: int, curr_depth: int = 0) -> None:
        if curr_depth >= depth:
            lst.append(random.choice([{1, 2, 3}, {"a": 1, "b": 2}, [1, 2, 3], (1, 2, 3)]))
            return

        for _ in range(n_elements):
            new_lst: List[Any] = []
            append_elem(new_lst, depth=depth, n_elements=n_elements, curr_depth=curr_depth + 1)
            lst.append(new_lst)

    lst: List[Any] = []
    append_elem(lst, depth=depth, n_elements=n_elements)
    return lst


class TestBigFile:
    THIS_DIR: Final = Path(__file__).parent
    TEST_FILES_DIR: Final = THIS_DIR / "test_files"

    @staticmethod
    def read_yaml_file(file_path: str) -> object:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)

    @pytest.fixture
    def sample(self, file_name: str) -> object:
        path = self.TEST_FILES_DIR / file_name
        return self.read_yaml_file(str(path))

    @pytest.mark.parametrize("file_name", ["big_file.yaml"])
    def test(self, file_name: str, sample: object) -> None:
        n = 10  # Number of executions
        total_time = timeit.timeit(lambda: data_type_tree_factory(sample, name="Example"), number=n)

        average_time = total_time / n
        assert average_time < 0.2


class TestLongContainers:
    def test_long_list(self) -> None:
        lst = [1] * 1_000_000
        n = 10  # Number of executions
        total_time = timeit.timeit(
            lambda: data_type_tree_factory(
                lst, name="Example", strategies=ParsingStrategies(check_max_n_elements_within_container=100)
            ),
            number=n,
        )

        average_time = total_time / n
        assert average_time < 0.02

    @pytest.mark.parametrize("strategy", ["dict", "Mapping"])
    def test_long_dict(self, strategy: Literal["dict", "Mapping"]) -> None:
        n_elements = 1_000_000
        dct = dict(zip(range(n_elements), range(n_elements)))
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
        assert average_time < 0.02


class TestDeepList:
    def test(self) -> None:
        n = 2
        lst = generate_tree_based_list(depth=8, n_elements=3)
        total_time = timeit.timeit(lambda: data_type_tree_factory(lst, name="Example"), number=n)
        average_time = total_time / n
        assert average_time < 1.5
