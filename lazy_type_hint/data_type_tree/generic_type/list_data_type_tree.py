from typing import Any
from collections.abc import Sequence

from typing_extensions import override

from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree, DataTypeTreeError
from lazy_type_hint.data_type_tree.generic_type.sequence_data_type_tree import (
    SequenceDataTypeTree,
)


class ListDataTypeTree(SequenceDataTypeTree):
    wraps = (list,)

    @override
    def _instantiate_children(self, data: Sequence[Any]) -> tuple[DataTypeTree, ...]:  # type: ignore
        return self.operations.instantiate_children(data, allow_repeated_children=False)

    @override
    def _get_str_top_node(self) -> str:
        if self.strategies.list_strategy == "list":
            container = "list"
        elif self.strategies.list_strategy == "Sequence":
            self.imports.add("Sequence")
            container = "Sequence"
        else:
            raise DataTypeTreeError(f"The chosen strategy ({self.strategies.list_strategy}) is not available.")
        self.imports.add("TypeAlias")
        return f"{self.name}: TypeAlias = {container}[{self.get_type_alias_children()}]"
