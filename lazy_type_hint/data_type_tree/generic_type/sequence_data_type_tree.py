from typing import Hashable, List

from typing_extensions import override

from lazy_type_hint.data_type_tree.generic_type.generic_data_type_tree import (
    GenericDataTypeTree,
)
from lazy_type_hint.data_type_tree.generic_type.set_and_sequence_operations import SetAndSequenceOperations


class SequenceDataTypeTree(GenericDataTypeTree):
    operations: SetAndSequenceOperations

    @override
    def __pre_child_instantiation__(self) -> None:
        self.operations = SetAndSequenceOperations(self)

    @override
    def _get_hash(self) -> Hashable:
        hashes: List[object] = []
        for child in self:
            hashes.append(child._get_hash())
        return frozenset(hashes)
