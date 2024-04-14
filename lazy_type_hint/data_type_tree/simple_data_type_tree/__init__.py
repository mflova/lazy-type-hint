from contextlib import suppress

from lazy_type_hint.data_type_tree.simple_data_type_tree.function_data_type_tree import (
    FunctionDataTypeTree as FunctionDataTypeTree,
)
from lazy_type_hint.data_type_tree.simple_data_type_tree.instance_data_type_tree import (
    InstanceDataTypeTree as InstanceDataTypeTree,
)

with suppress(ImportError):
    from lazy_type_hint.data_type_tree.simple_data_type_tree.pandas_series_data_type_tree import (
        PandasSeriesDataTypeTree as PandasSeriesDataTypeTree,
    )
from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import (
    SimpleDataTypeTree as SimpleDataTypeTree,
)
from lazy_type_hint.data_type_tree.simple_data_type_tree.type_data_type_tree import (
    TypeDataTypeTree as TypeDataTypeTree,
)
