from contextlib import suppress
from pathlib import Path
from typing import Final

import pytest

from dynamic_pyi_generator.pyi_generator import PyiGenerator
from dynamic_pyi_generator.testing_tools import Mypy


class TestPyiGenerator:
    DATA_TEST_DIR: Final = Path(__file__).parent / "test_files"

    @pytest.fixture
    def pyi_generator(self) -> PyiGenerator:
        return PyiGenerator()

    @pytest.fixture
    def mypy(self) -> Mypy:
        return Mypy()

    @pytest.fixture(autouse=True)
    def _teardown(self, pyi_generator: PyiGenerator):
        yield
        pyi_generator.reset()

    @pytest.mark.parametrize(
        "file, expected_mypy_success",
        (["ok.py", True], ["key_missing.py", False], ["wrong_value_type", False]),
    )
    def test(self, file: str, expected_mypy_success: bool, mypy: Mypy) -> None:
        """
        Test the given file by executing its content, using mypy and assert the result.

        Args:
            file (str): The path to the file to be tested.
            expected_mypy_success (bool): The expected result of mypy's success.
            mypy (Mypy): The Mypy instance used to run mypy.
        """
        file_path = self.DATA_TEST_DIR / file

        with suppress(Exception):
            exec(file_path.read_text())
        result = mypy.run(file_path)
        assert result.success == expected_mypy_success, result.stdout
