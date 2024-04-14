from typing import Final

import pandas as pd
import pytest

from lazy_type_hint.data_type_tree.simple_data_type_tree.pandas_series_data_type_tree import (
    PandasSeriesDataTypeTree as PandasSeriesDataTypeTree,
)


class TestSeries:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "data, expected_str",
        [
            [pd.Series(), f"{NAME}: TypeAlias = pd.Series"],
            [pd.Series([1, 2, 3]), f"{NAME}: TypeAlias = pd.Series"],
        ],
    )
    def test_get_str_top_node(self, data: object, expected_str: str) -> None:
        tree = PandasSeriesDataTypeTree(data, self.NAME)
        assert expected_str == tree.get_str_top_node()
        assert "TypeAlias" in tree.imports
