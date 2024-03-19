from pathlib import Path
from typing import Final

import pytest

from dynamic_pyi_generator.pyi_generator import PyiGenerator, PyiGeneratorError
from dynamic_pyi_generator.testing_tools import Mypy


class TestPyiGenerator:
    DATA_TEST_DIR: Final = Path(__file__).parent / "test_files"

    @pytest.fixture
    def pyi_generator(self) -> PyiGenerator:
        return PyiGenerator()

    def expected_mypy_succes(self, file: str) -> bool:
        if file.startswith("ok"):
            return True
        elif file.startswith("nok"):
            return False
        else:
            raise ValueError(f"File must be start with nok or ok. Given one is: {file}")

    @pytest.fixture(autouse=True)
    def _teardown(self, pyi_generator: PyiGenerator) -> Any:
        pyi_generator.reset()
        yield
        pyi_generator.reset()

    @pytest.mark.parametrize(
        "file",
        (
            "ok_list.py",
            "ok_append_list_as_any_or_object.py",
            "ok_list.py",
            "ok_dict.py",
            "ok_str.py",
            "ok_float.py",
            "ok_int.py",
            "ok_set.py",
            "ok_frozenset.py",
            "ok_nested_list.py",
            "nok_append_list_wrong_type.py",
            "nok_append_sequence.py",
            "nok_frozen_set.py",
            "nok_key_missing.py",
            "nok_list.py",
            "nok_modify_mapping.py",
            "nok_list.py",
        ),
    )
    def test_generated_interface(self, file: str, mypy: Mypy) -> None:
        """
        Test the given file by executing its content, using mypy and assert the result.

        Args:
            file (str): The path to the file to be tested.
            mypy (Mypy): The Mypy instance used to run mypy.
        """
        expected_mypy_success = self.expected_mypy_succes(file)
        file_path = self.DATA_TEST_DIR / file

        if expected_mypy_success:
            exec(file_path.read_text())
        else:
            with suppress(Exception):
                exec(file_path.read_text())
        result = mypy.run(file_path, ignore_errors="Overloaded")
        assert result.success == expected_mypy_success, str(result)

    @pytest.mark.parametrize("file", (["nok_non_compliant_dictionary.py"]))
    def test_exceptions_raised(self, file: str) -> None:
        file_path = self.DATA_TEST_DIR / file
        with pytest.raises(PyiGeneratorError):
            exec(file_path.read_text())
