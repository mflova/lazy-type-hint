from contextlib import suppress
from pathlib import Path
from typing import Any, Final

import pytest

from dynamic_pyi_generator.pyi_generator import PyiGenerator, PyiGeneratorError
from dynamic_pyi_generator.testing_tools import Mypy


class TestPyiGenerator:
    DATA_TEST_DIR: Final = Path(__file__).parent / "test_files"

    @pytest.fixture
    def pyi_generator(self) -> PyiGenerator:
        return PyiGenerator()

    @pytest.fixture(autouse=True)
    def _teardown(self, pyi_generator: PyiGenerator) -> Any:
        pyi_generator.reset()
        yield
        pyi_generator.reset()

    @pytest.mark.parametrize(
        "file, expected_mypy_success",
        (
            ["ok_list.py", True],
            ["ok_dict.py", True],
            ["ok_str.py", True],
            ["ok_float.py", True],
            ["ok_int.py", True],
            ["ok_set.py", True],
            ["ok_frozenset.py", True],
            ["ok_nested_list.py", True],
            ["not_ok_list.py", False],
            ["key_missing.py", False],
            ["wrong_value_type.py", False],
        ),
    )
    def test_generated_interface_is_ok(
        self, file: str, expected_mypy_success: bool, mypy: Mypy
    ) -> None:
        """
        Test the given file by executing its content, using mypy and assert the result.

        Args:
            file (str): The path to the file to be tested.
            expected_mypy_success (bool): The expected result of mypy's success.
            mypy (Mypy): The Mypy instance used to run mypy.
        """
        file_path = self.DATA_TEST_DIR / file

        if expected_mypy_success:
            exec(file_path.read_text())
        else:
            with suppress(Exception):
                exec(file_path.read_text())
        result = mypy.run(file_path, ignore_errors="Overloaded")
        assert result.success == expected_mypy_success, str(result)

    @pytest.mark.parametrize("file", (["non_compliant_dictionary.py"]))
    def test_exceptions_raised(self, file: str) -> None:
        file_path = self.DATA_TEST_DIR / file
        with pytest.raises(PyiGeneratorError):
            exec(file_path.read_text())
