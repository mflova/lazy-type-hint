import timeit
from pathlib import Path
from typing import Final

import pytest
import yaml

from lazy_type_hint.data_type_tree import data_type_tree_factory


class TestPerformance:
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
    def test_performance(self, file_name: str, sample: object) -> None:  # noqa: ARG002
        n = 10  # Number of executions
        total_time = timeit.timeit(lambda: data_type_tree_factory(sample, name="Example"), number=n)

        average_time = total_time / n
        assert average_time < 0.2
