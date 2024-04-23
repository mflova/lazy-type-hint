import pandas as pd
from typing_extensions import override

from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import SimpleDataTypeTree


class PandasSeriesDataTypeTree(SimpleDataTypeTree):
    wraps = (pd.Series,)

    @override
    def _get_str_top_node(self) -> str:
        self.imports.add("pandas").add("TypeAlias")
        return f"{self.name}: TypeAlias = pd.Series"
