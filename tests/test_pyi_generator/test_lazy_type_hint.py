from pathlib import Path
from typing import Union

import pytest
import yaml

from lazy_type_hint.generators.lazy_type_hint import LazyTypeHint


@pytest.fixture
def lazy_type_hint() -> LazyTypeHint:
    return LazyTypeHint()


class TestLazyTypeHintFromData:
    @pytest.mark.parametrize(
        "data",
        (
            {"key": "value"},
            [1, 2, 3],
            {"nested": {"key": "value"}},
            [4, 5, 6],
        ),
    )
    def test_from_data(self, lazy_type_hint: LazyTypeHint, data: object, tmp_path: str) -> None:
        result = lazy_type_hint.from_data(data, class_name="Example")
        result.as_string()
        result.to_file(Path(tmp_path) / "file.py")


class TestLazyTypeHintFromYamlFile:
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
        self,
        lazy_type_hint: LazyTypeHint,
        data: object,
        yaml_file: Path,
        tmp_path: str,
    ) -> None:
        result = lazy_type_hint.from_yaml_file(loader=self.yaml_file_loader, path=yaml_file, class_name="Example")
        result.as_string()
        result.to_file(Path(tmp_path) / "file.py")
