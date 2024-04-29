from typing import Final

import pandas as pd
import pytest

from lazy_type_hint.data_type_tree.generic_type.pandas_series_data_type_tree import PandasSeriesDataTypeTree
from lazy_type_hint.strategies import ParsingStrategies


class TestSeries:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "data, expected_str",
        [
            [pd.Series(), f"{NAME}: TypeAlias = pd.Series[Any]"],
            [pd.Series([1, 2, 3]), f"{NAME}: TypeAlias = pd.Series[int]"],
            [pd.Series([1, 2, 1.1]), f"{NAME}: TypeAlias = pd.Series[float]"],
            [pd.Series([1, 2, "a"]), f"{NAME}: TypeAlias = pd.Series[Union[int, str]]"],
            [pd.Series([1, 2, []]), f"{NAME}: TypeAlias = pd.Series[Union[{NAME}List, int]]"],
        ],
    )
    def test_get_str_top_node(self, data: object, expected_str: str) -> None:
        tree = PandasSeriesDataTypeTree(
            data, self.NAME, strategies=ParsingStrategies(min_height_to_define_type_alias=0)
        )
        assert expected_str == tree.get_str_top_node()
        assert "TypeAlias" in tree.imports
