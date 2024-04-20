from typing import TYPE_CHECKING, Hashable, List

from typing_extensions import Self, override

from lazy_type_hint.data_type_tree.generic_type.generic_data_type_tree import (
    GenericDataTypeTree,
)
from lazy_type_hint.data_type_tree.generic_type.set_and_sequence_operations import SetAndSequenceOperations

if TYPE_CHECKING:
    from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree


class SequenceDataTypeTree(GenericDataTypeTree):
    operations: SetAndSequenceOperations

    _iterator: int

    @override
    def __pre_child_instantiation__(self) -> None:
        self.operations = SetAndSequenceOperations(self)

    @override
    def _get_hash(self) -> Hashable:
        hashes: List[object] = []
        for child in self:
            hashes.append(child._get_hash())
        return frozenset(hashes)

    @override
    def __iter__(self) -> "Self":
        self._iterator = 0  # Reset the index to zero when starting a new iteration
        return self

    @override
    def __next__(self) -> "DataTypeTree":
        if self._iterator < len(self.children):
            element = list(self.children)[self._iterator]
            self._iterator += 1
            return element  # type: ignore
        else:
            raise StopIteration
