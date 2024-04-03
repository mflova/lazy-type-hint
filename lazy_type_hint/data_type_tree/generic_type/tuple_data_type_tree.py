from typing import Any, Hashable, List, Sequence, Tuple

from typing_extensions import override

from lazy_type_hint.data_type_tree import DataTypeTree
from lazy_type_hint.data_type_tree.generic_type.sequence_data_type_tree import SequenceDataTypeTree


class TupleDataTypeTree(SequenceDataTypeTree):
    wraps = tuple
    original_data = Tuple[object, ...]

    @override
    def _instantiate_children(self, data: Sequence[Any]) -> Tuple[DataTypeTree, ...]:  # type: ignore
        if self.strategies.tuple_size_strategy == "fixed":
            return self.operations.instantiate_children(data, allow_repeated_children=True)
        else:
            return self.operations.instantiate_children(data, allow_repeated_children=False)

    @override
    def _get_str_top_node(self) -> str:
        self.imports.add("tuple")
        return f"{self.name} = Tuple[{self.get_type_alias_children()}]"

    @override
    def get_type_alias_children(self) -> str:
        if self.strategies.tuple_size_strategy == "fixed":
            child_types = self._get_types(remove_repeated=False)
        else:
            child_types = self._get_types(remove_repeated=True)
        return self._format_types(child_types)

    @override
    def _format_types(self, child_types: Sequence[str]) -> str:
        if len(child_types) == 1 and "Any" in child_types:
            self.imports.add("Any")
            return "Any, ..."

        if self.strategies.tuple_size_strategy == "fixed":
            return f"{', '.join(child_types)}"
        else:
            names_set = set(child_types)
            if len(names_set) == 1:
                return f"{next(iter(names_set))}, ..."
            self.imports.add("Union")
            return f"Union[{', '.join(sorted(names_set))}], ..."

    @override
    def _get_hash(self) -> Hashable:
        if self.strategies.tuple_size_strategy == "any size":
            return super()._get_hash()
        else:
            hashes: List[object] = []
            for child in self:
                hashes.append(child._get_hash())
            return tuple(hashes)
