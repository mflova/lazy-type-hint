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
with suppress(ImportError):
    from lazy_type_hint.data_type_tree.simple_data_type_tree.numpy_data_type_tree import (
        NumpyDataTypeTree as NumpyDataTypeTree,
    )
from lazy_type_hint.data_type_tree.simple_data_type_tree.io_data_type_tree import IoDataTypeTree as IoDataTypeTree
from lazy_type_hint.data_type_tree.simple_data_type_tree.module_data_type_tree import (
    ModuleTypeDataTypeTree as ModuleTypeDataTypeTree,
)
from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import (
    SimpleDataTypeTree as SimpleDataTypeTree,
)
from lazy_type_hint.data_type_tree.simple_data_type_tree.type_data_type_tree import (
    TypeDataTypeTree as TypeDataTypeTree,
)
