from types import MappingProxyType

from lazy_type_hint.data_type_tree.generic_type.mapping_data_type_tree import MappingDataTypeTree


class MappingProxyDataTypeTree(MappingDataTypeTree):
    wraps = MappingProxyType
