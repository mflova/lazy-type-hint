from typing import Any, Hashable, Literal, Sequence, Set, Tuple

from typing_extensions import override

from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
from lazy_type_hint.data_type_tree.generic_type.generic_data_type_tree import (
    GenericDataTypeTree,
)
from lazy_type_hint.data_type_tree.generic_type.set_and_sequence_operations import SetAndSequenceOperations


class SetDataTypeTree(GenericDataTypeTree):
    wraps = (frozenset, set)
    children: Sequence[DataTypeTree]
    operations: SetAndSequenceOperations

    @override
    def __pre_child_instantiation__(self) -> None:
        self.operations = SetAndSequenceOperations(self)

    @override
    def _instantiate_children(self, data: Sequence[Any]) -> Tuple[DataTypeTree, ...]:  # type: ignore
        return self.operations.instantiate_children(data, allow_repeated_children=False)

    @override
    def _get_str_top_node(self) -> str:
        container: Literal["FrozenSet", "set"] = "FrozenSet" if self.holding_type is frozenset else "set"
        self.imports.add(container)

        if container == "FrozenSet":
            return f"{self.name} = FrozenSet[{self.get_type_alias_children()}]"
        return f"{self.name} = Set[{self.get_type_alias_children()}]"

    @override
    def _get_hash(self) -> Hashable:
        hashes: Set[object] = set()
        for child in self:
            hashes.add(child._get_hash())
        return frozenset(hashes)
