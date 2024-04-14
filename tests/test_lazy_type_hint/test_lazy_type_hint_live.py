from pathlib import Path
from typing import Final, Union

import pytest
import yaml

from lazy_type_hint.generators.lazy_type_hint_live import LazyTypeHintLive
from lazy_type_hint.utils import Mypy


@pytest.mark.usefixtures("_serial")
@pytest.mark.skipif(not Mypy.is_available(), reason="Mypy must be available via terminal.")
class TestLazyTypeHintLive:
    DATA_TEST_DIR: Final = Path(__file__).parent / "test_files"

    def expected_mypy_succes(self, file: str) -> bool:
        if file.startswith("ok"):
            return True
        elif file.startswith("nok"):
            return False
        else:
            raise ValueError(f"File must be start with nok or ok. Given one is: {file}")

    @pytest.mark.parametrize(
        "file",
        (
            "ok_list.py",
            "ok_dict.py",
            "ok_str.py",
            "ok_float.py",
            "ok_int.py",
            "ok_set.py",
            "ok_pandas_dataframe.py",
            "ok_frozenset.py",
            "ok_nested_list.py",
            "nok_append_list_wrong_type.py",
            "nok_append_sequence.py",
            "nok_frozen_set.py",
            "nok_key_missing.py",
            "nok_list.py",
            "nok_modify_mapping.py",
            "nok_pandas_dataframe.py",
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
        file_content = file_path.read_text()
        exec(file_content)

        result = mypy.scan_file(file_path, strict=True, ignore_errors=["Overloaded"])
        assert result.success == expected_mypy_success, str(result)


@pytest.mark.usefixtures("_serial")
class TestLazyTypeHintLiveFromYaml:
    @pytest.fixture
    def yaml_file(self, data: object, tmp_path: str) -> Path:
        path = Path(tmp_path) / "file.yaml"
        with open(path, mode="w", encoding="UTF-8") as f:
            yaml.dump(data, f)
        return path

    @staticmethod
    def yaml_file_loader(path: Union[Path, str]) -> object:
        with open(path) as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    @pytest.fixture
    def lazy_type_hint(self) -> LazyTypeHintLive:
        return LazyTypeHintLive()

    @pytest.mark.parametrize(
        "data",
        (
            {"key": "value"},
            [1, 2, 3],
            {"nested": {"key": "value"}},
            [4, 5, 6],
        ),
    )
    def test_from_yaml_file(
        self, lazy_type_hint: LazyTypeHintLive, data: object, yaml_file: Path, tmp_path: str
    ) -> None:
        lazy_type_hint.reset()
        lazy_type_hint.from_yaml_file(loader=self.yaml_file_loader, path=yaml_file, class_name="Example")
