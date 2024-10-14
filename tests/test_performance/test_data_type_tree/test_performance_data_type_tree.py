from pathlib import Path
from typing import Any, Callable, Final

import pytest
import yaml
from pytest_benchmark.fixture import BenchmarkFixture

from lazy_type_hint.data_type_tree import data_type_tree_factory


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
    def test_instantiation(self, file_name: str, sample: object, benchmark: BenchmarkFixture) -> None:
        benchmark(lambda: data_type_tree_factory(sample, name="Example"))
        assert benchmark.stats.stats.mean < 0.2

    @pytest.mark.parametrize("file_name", ["big_file.yaml"])
    def test_get_str(self, file_name: str, sample: object, benchmark: BenchmarkFixture) -> None:
        tree = data_type_tree_factory(sample, name="Example")

        benchmark(lambda: tree.get_str_all_nodes(include_imports=True))
        assert benchmark.stats.stats.mean < 8e-5


class TestHash:
    def test(self, generate_tree_based_list: Callable[[int, int], list[Any]], benchmark: BenchmarkFixture) -> None:
        lst = generate_tree_based_list(depth=10, n_elements=3)  # type: ignore

        def launcher() -> None:
            tree = data_type_tree_factory(lst, name="Example")
            benchmark(lambda: hash(tree))

        launcher()
        assert benchmark.stats.stats.mean < 2e-5
