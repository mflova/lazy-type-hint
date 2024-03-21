from types import MappingProxyType

from dynamic_pyi_generator.data_type_tree.generic_type.mapping_data_type_tree import MappingDataTypeTree


class MappingProxyDataTypeTree(MappingDataTypeTree):
    wraps = MappingProxyType
