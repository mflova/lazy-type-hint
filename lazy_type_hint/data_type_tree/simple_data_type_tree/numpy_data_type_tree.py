import numpy as np
from numpy.typing import NDArray
from typing_extensions import override

from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import SimpleDataTypeTree


class NumpyDataTypeTree(SimpleDataTypeTree):
    wraps = (np.ndarray,)
    data: NDArray[np.generic]

    @override
    def _get_str_top_node(self) -> str:
        self.imports.add("NDArray").add("numpy").add("TypeAlias")
        return f'{self.name}: TypeAlias = "NDArray[np.{self.data.dtype}]"'
