from typing import Any, Sequence

from typing_extensions import override

from dynamic_pyi_generator.data_type_tree.data_type_tree import DataTypeTree
from dynamic_pyi_generator.data_type_tree.generic_type.generic_data_type_tree import (
    GenericDataTypeTree,
    get_childs_for_set_and_sequence,
)


class SequenceDataTypeTree(GenericDataTypeTree):
    @override
    def _get_childs(self, data: Sequence[Any]) -> Sequence[DataTypeTree]:  # type: ignore
        return get_childs_for_set_and_sequence(self, data)
