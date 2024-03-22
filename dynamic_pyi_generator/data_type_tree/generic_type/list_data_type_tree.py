from typing import Any, Sequence, Tuple

from typing_extensions import override

from dynamic_pyi_generator.data_type_tree.data_type_tree import DataTypeTree, DataTypeTreeError
from dynamic_pyi_generator.data_type_tree.generic_type.generic_data_type_tree import get_childs_for_set_and_sequence
from dynamic_pyi_generator.data_type_tree.generic_type.sequence_data_type_tree import (
    SequenceDataTypeTree,
)


class ListDataTypeTree(SequenceDataTypeTree):
    wraps = list

    @override
    def _get_childs(self, data: Sequence[Any]) -> Tuple[DataTypeTree, ...]:  # type: ignore
        return get_childs_for_set_and_sequence(self, data, allow_repeated_childs=False)

    @override
    def _get_str_py(self) -> str:
        if self.strategies.list_strategy == "List":
            self.imports.add("from typing import List")
            container = "List"
        elif self.strategies.list_strategy == "Sequence":
            self.imports.add("from typing import Sequence")
            container = "Sequence"
        else:
            raise DataTypeTreeError(f"The chosen strategy ({self.strategies.list_strategy}) is not available.")
        return f"{self.name} = {container}[{self.get_type_alias_childs()}]"
