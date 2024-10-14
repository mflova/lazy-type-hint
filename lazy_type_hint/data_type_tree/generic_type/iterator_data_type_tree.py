from typing import Any
from collections.abc import Iterator, Sequence

from typing_extensions import override

from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
from lazy_type_hint.data_type_tree.generic_type.sequence_data_type_tree import (
    SequenceDataTypeTree,
)


class IteratorDataTypeTree(SequenceDataTypeTree):
    wraps = (Iterator,)

    @override
    def _instantiate_children(self, data: Sequence[Any]) -> tuple[DataTypeTree, ...]:  # type: ignore
        return self.operations.instantiate_children(data, allow_repeated_children=False)

    @override
    def _get_str_top_node(self) -> str:
        self.imports.add("Iterator").add("TypeAlias")
        container = "Iterator"
        return f"{self.name}: TypeAlias = {container}[{self.get_type_alias_children()}]"
