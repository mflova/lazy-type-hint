from typing import Final

import numpy as np
import pytest
from numpy.typing import NDArray

from lazy_type_hint.data_type_tree.simple_data_type_tree.numpy_data_type_tree import NumpyDataTypeTree


class TestGetStr:
    name: Final = "Example"

    @pytest.mark.parametrize(
        "input_arr, expected_str",
        [
            (np.array([1]), f"{name}: TypeAlias = NDArray[np.int32]"),
            (np.array([1.0]), f"{name}: TypeAlias = NDArray[np.float64]"),
            (np.zeros((2, 2), dtype=np.complex128), f"{name}: TypeAlias = NDArray[np.complex128]"),
        ],
    )
    def test_get_str_top_node(self, input_arr: NDArray[np.generic], expected_str: str) -> None:
        tree = NumpyDataTypeTree(input_arr, name=self.name)
        assert expected_str == tree.get_str_top_node()
        assert "numpy" in tree.imports
        assert "NDArray" in tree.imports
        assert "TypeAlias" in tree.imports
