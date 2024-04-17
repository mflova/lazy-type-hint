import random
import time
import timeit
from pathlib import Path
from typing import Any, Final, List

import pytest
import yaml

from lazy_type_hint.data_type_tree import data_type_tree_factory


class TestPerformanceBigFile:
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

class TestPerformanceBigList:
    def test(self) -> None:
        lst = [1]*1_000_000
        n = 10  # Number of executions
        total_time = timeit.timeit(lambda: data_type_tree_factory(lst, name="Example"), number=n)

        average_time = total_time / n
        assert average_time < 0.2


class TestPerformanceHash:
    def generate_tree_based_list(self, depth: int, n_elements: int) -> List[Any]:
        def append_elem(lst: List[Any], depth: int, n_elements: int, curr_depth: int = 0) -> None:
            if curr_depth >= depth:
                lst.append(random.choice([{1,2,3}, {"a": 1, "b": 2}, [1,2,3], (1,2,3)]))
                return

            for i in range(n_elements):
                new_lst: List[Any] = []
                append_elem(new_lst, depth=depth, n_elements=n_elements, curr_depth=curr_depth+1)
                lst.append(new_lst)
        lst = []
        append_elem(lst, depth=depth, n_elements=n_elements)
        return lst

    def test(self) -> None:
        lst = self.generate_tree_based_list(depth=10, n_elements=3)
        tree = data_type_tree_factory(lst, name="Example")

        time_before_cache = timeit.timeit(lambda: hash(tree), number=1)
        time_after_cache = timeit.timeit(lambda: hash(tree), number=1)
        
        assert time_after_cache < time_before_cache/1_000