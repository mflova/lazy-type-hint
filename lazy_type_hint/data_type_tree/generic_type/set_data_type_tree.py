from typing import Any, Literal
from collections.abc import Hashable, Sequence

from typing_extensions import Self, override

from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
from lazy_type_hint.data_type_tree.generic_type.generic_data_type_tree import (
    GenericDataTypeTree,
)
from lazy_type_hint.data_type_tree.generic_type.set_and_sequence_operations import SetAndSequenceOperations


class SetDataTypeTree(GenericDataTypeTree):
    wraps = (frozenset, set)
    children: Sequence[DataTypeTree]
    operations: SetAndSequenceOperations

    _iterator: int

    @override
    def __pre_child_instantiation__(self) -> None:
        self.operations = SetAndSequenceOperations(self)

    @override
    def _instantiate_children(self, data: Sequence[Any]) -> tuple[DataTypeTree, ...]:  # type: ignore
        return self.operations.instantiate_children(data, allow_repeated_children=False)

    @override
    def _get_str_top_node(self) -> str:
        self.imports.add("TypeAlias")

        container: Literal["frozenset", "set"] = "frozenset" if self.holding_type is frozenset else "set"
        if container == "frozenset":
            return f"{self.name}: TypeAlias = frozenset[{self.get_type_alias_children()}]"
        return f"{self.name}: TypeAlias = set[{self.get_type_alias_children()}]"

    @override
    def _get_hash(self) -> Hashable:
        hashes: set[object] = set()
        for child in self:
            hashes.add(child._get_hash())
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
            return element
        else:
            raise StopIteration
