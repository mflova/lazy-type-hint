from typing import Any, List, Sequence, Tuple

from typing_extensions import override

from dynamic_pyi_generator.data_type_tree import DataTypeTree
from dynamic_pyi_generator.data_type_tree.generic_type.generic_data_type_tree import get_childs_for_set_and_sequence
from dynamic_pyi_generator.data_type_tree.generic_type.sequence_data_type_tree import SequenceDataTypeTree


class TupleDataTypeTree(SequenceDataTypeTree):
    wraps = tuple

    @override
    def _get_childs(self, data: Sequence[Any]) -> Tuple[DataTypeTree, ...]:  # type: ignore
        if self.strategies.tuple_size_strategy == "fixed":
            return get_childs_for_set_and_sequence(self, data, allow_repeated_childs=True)
        else:
            return get_childs_for_set_and_sequence(self, data, allow_repeated_childs=False)

    @override
    def _get_str_py(self) -> str:
        self.imports.add("from typing import Tuple")
        return f"{self.name} = Tuple[{self.get_type_alias_childs()}]"

    @override
    def get_type_alias_childs(self) -> str:
        if self.strategies.tuple_size_strategy == "fixed":
            child_types = self._get_types(remove_repeated=False)
        else:
            child_types = self._get_types(remove_repeated=True)
        return self._format_types(child_types)

    @override
    def _format_types(self, child_types: Sequence[str]) -> str:
        if len(child_types) == 1 and "Any" in child_types:
            self.imports.add("from typing import Any")
            return "Any, ..."

        if self.strategies.tuple_size_strategy == "fixed":
            return f"{', '.join(child_types)}"
        else:
            names_set = set(child_types)
            if len(names_set) == 1:
                return f"{next(iter(names_set))}, ..."
            self.imports.add("from typing import Union")
            return f"Union[{', '.join(sorted(names_set))}], ..."

    @override
    def _get_hash(self) -> object:
        if self.strategies.tuple_size_strategy == "...":
            return super()._get_hash()
        else:
            hashes: List[object] = []
            for child in self:
                hashes.append(child._get_hash())
            return tuple(hashes)
