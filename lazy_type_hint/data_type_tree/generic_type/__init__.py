from contextlib import suppress

from lazy_type_hint.data_type_tree.generic_type.dict_data_type_tree import DictDataTypeTree as DictDataTypeTree
from lazy_type_hint.data_type_tree.generic_type.list_data_type_tree import ListDataTypeTree as ListDataTypeTree
from lazy_type_hint.data_type_tree.generic_type.mapping_data_type_tree import (
    MappingDataTypeTree as MappingDataTypeTree,
)

with suppress(ImportError):
    from lazy_type_hint.data_type_tree.generic_type.pandas_data_frame_data_type_tree import (
        PandasDataFrameDataTypeTree as PandasDataFrameDataTypeTree,
    )
from lazy_type_hint.data_type_tree.generic_type.iterator_data_type_tree import (
    IteratorDataTypeTree as IteratorDataTypeTree,
)
from lazy_type_hint.data_type_tree.generic_type.mapping_proxy_data_type_tree import (
    MappingProxyDataTypeTree as MappingProxyDataTypeTree,
)
from lazy_type_hint.data_type_tree.generic_type.set_data_type_tree import SetDataTypeTree as SetDataTypeTree
from lazy_type_hint.data_type_tree.generic_type.tuple_data_type_tree import (
    TupleDataTypeTree as TupleDataTypeTree,
)
