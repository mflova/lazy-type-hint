from itertools import islice
from types import MappingProxyType
from typing import Any

from typing_extensions import override

from lazy_type_hint.data_type_tree.generic_type.mapping_data_type_tree import MappingDataTypeTree


class MappingProxyDataTypeTree(MappingDataTypeTree):
    wraps = (MappingProxyType,)
    data: MappingProxyType[Any, Any]

    @override
    def __pre_child_instantiation__(self) -> None:
        if check_n_max := self.strategies.check_max_n_elements_within_container:
            self.data = MappingProxyType(dict(islice(self.data.items(), check_n_max)))
