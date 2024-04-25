from pathlib import Path
from typing import Any, Final, Literal, Mapping, Union, cast

import pytest
import yaml

from lazy_type_hint.generators.lazy_type_hint_live import LazyTypeHintLive, LazyTypeHintLiveError
from lazy_type_hint.strategies import ParsingStrategies
from lazy_type_hint.utils import Mypy


def yaml_file_loader(path: Union[Path, str]) -> object:
    with open(path) as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


@pytest.fixture
def lazy_type_hint_live() -> LazyTypeHintLive:
    return LazyTypeHintLive()


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
            "ok_pandas_series.py",
            "ok_numpy.py",
            "ok_frozenset.py",
            "ok_nested_list.py",
            "nok_append_list_wrong_type.py",
            "nok_append_sequence.py",
            "nok_frozen_set.py",
            "nok_key_missing.py",
            "nok_list.py",
            "nok_modify_mapping.py",
            "nok_pandas_dataframe.py",
            "nok_pandas_series.py",
            "nok_numpy.py",
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
class TestLazyTypeHintLiveValidationFromData:
    name: Final = "Example"

    @pytest.mark.parametrize(
        "data1, data2, expected_ok",
        [
            ([1, 2], [1, 3], True),
            ([1, 2], [1, "2"], False),
        ],
    )
    @pytest.mark.parametrize("if_type_hint_exists", ["overwrite", "validate"])
    def test_validation(
        self, data1: object, data2: object, if_type_hint_exists: Literal["overwrite", "validate"], expected_ok: bool
    ) -> None:
        LazyTypeHintLive(if_type_hint_exists=if_type_hint_exists).from_data(data1, class_name=self.name)
        type_hints_before = self.read_type_hints()
        if if_type_hint_exists == "overwrite" or expected_ok:
            LazyTypeHintLive(if_type_hint_exists=if_type_hint_exists).from_data(data2, class_name=self.name)
            type_hints_after = self.read_type_hints()
            if if_type_hint_exists == "overwrite" and not expected_ok:
                assert type_hints_before != type_hints_after, "Overwrite mode does not overwrite existing type hints"
            if if_type_hint_exists == "validate":
                assert type_hints_before == type_hints_after, "Validate mode does change the existing type hints"
        else:
            with pytest.raises(LazyTypeHintLiveError):
                LazyTypeHintLive(if_type_hint_exists=if_type_hint_exists).from_data(data2, class_name=self.name)
            assert type_hints_before == self.read_type_hints(), "Validate mode does change the existing type hints"
            LazyTypeHintLive.reset()
            LazyTypeHintLive(if_type_hint_exists=if_type_hint_exists).from_data(data2, class_name=self.name)

    def test_validation_different_names(self) -> None:
        LazyTypeHintLive(if_type_hint_exists="overwrite").from_data([1, 2], class_name="Example1")
        LazyTypeHintLive(if_type_hint_exists="validate").from_data([1, "a"], class_name="Example2")

    def test_validation_different_strategies(self) -> None:
        LazyTypeHintLive(
            if_type_hint_exists="validate", strategies=ParsingStrategies(list_strategy="Sequence")
        ).from_data([1, 2], class_name="Example")
        with pytest.raises(LazyTypeHintLiveError):
            LazyTypeHintLive(
                if_type_hint_exists="validate", strategies=ParsingStrategies(list_strategy="list")
            ).from_data([1, 2], class_name="Example")

    def read_type_hints(self) -> str:
        return Path(LazyTypeHintLive._custom_class_dir_path / f"{self.name}.py").read_text(encoding="utf-8")


@pytest.mark.usefixtures("_serial")
class TestLazyTypeHintLiveValidationFromYaml:
    name: Final = "Example"

    def test_validation_yaml_despite_docstrings(self, tmp_path: str) -> None:
        data1 = """
values:
    lst: [1,2,3]
"""

        data2 = """
values:
    # This is a list
    lst: [1,2,3]
"""
        file_path1 = Path(tmp_path) / "file1.yaml"
        file_path2 = Path(tmp_path) / "file2.yaml"

        self.save_yaml(data1, file_path1)
        self.save_yaml(data2, file_path2)

        LazyTypeHintLive(if_type_hint_exists="validate").from_yaml_file(
            loader=self.load_yaml, path=file_path1, class_name=self.name
        )
        LazyTypeHintLive(if_type_hint_exists="validate").from_yaml_file(
            loader=self.load_yaml, path=file_path2, class_name=self.name
        )

    @staticmethod
    def save_yaml(data: object, path: Path) -> None:
        with open(path, "w") as f:
            yaml.dump(data, f)

    @staticmethod
    def load_yaml(path: Path) -> object:
        with open(path) as f:
            return yaml.load(f, Loader=yaml.SafeLoader)


@pytest.mark.usefixtures("_serial")
class TestLazyTypeHintLiveFromYaml:
    @pytest.fixture
    def yaml_file(self, data: object, tmp_path: str) -> Path:
        path = Path(tmp_path) / "file.yaml"
        with open(path, mode="w", encoding="UTF-8") as f:
            yaml.dump(data, f)
        return path

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
        self, lazy_type_hint_live: LazyTypeHintLive, data: object, yaml_file: Path, tmp_path: str
    ) -> None:
        lazy_type_hint_live.reset()
        lazy_type_hint_live.from_yaml_file(loader=yaml_file_loader, path=yaml_file, class_name="Example")


@pytest.mark.usefixtures("_serial")
class TestLazyTypeHintFromYamlFileMutation:
    CONTENT_FILE: Final = """---
# Comment for level1
level1:
  # Comment for list1
  list1:
    - item1
    - item2
    - item3
  list2:
    # Non valid comment for subitem1
    - subitem1:  # Comment for subitem1
        # Comment for subkey1
        subkey1: subvalue1  # [mm]
      # Comment not valid for subkey1
        subkey2: subvalue2#Not a comment
    - subitem2:
        subkey3: subvalue3
        subkey4: subvalue4
"""

    @pytest.fixture
    def yaml_file(self, tmp_path: str) -> Path:
        path = Path(tmp_path) / "file.yaml"
        with open(path, mode="w", encoding="UTF-8") as f:
            yaml.dump(self.CONTENT_FILE, f)
        return path

    @pytest.fixture
    def original_content_of_yaml_file(self, yaml_file: Path) -> Mapping[str, Any]:
        with open(yaml_file) as f:
            return cast(Mapping[str, Any], yaml.load(f, Loader=yaml.FullLoader))

    def test_from_yaml_file(
        self,
        lazy_type_hint_live: LazyTypeHintLive,
        yaml_file: Path,
        original_content_of_yaml_file: Mapping[str, Any],
    ) -> None:
        output = lazy_type_hint_live.from_yaml_file(loader=yaml_file_loader, path=yaml_file, class_name="Example")
        assert original_content_of_yaml_file == output, "The YAML data was mutated"
