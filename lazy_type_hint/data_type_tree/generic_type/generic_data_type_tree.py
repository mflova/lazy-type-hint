from abc import abstractmethod
from typing import (
    final,
)
from collections.abc import Hashable, Iterable, Sequence

from typing_extensions import override

from lazy_type_hint.data_type_tree.data_type_tree import ChildrenStructure, DataTypeTree


class GenericDataTypeTree(DataTypeTree):
    """Tree that holds any kind of object that must contain other inner structures (children)."""

    children: ChildrenStructure[DataTypeTree]

    @abstractmethod
    def _instantiate_children(self, data: object) -> ChildrenStructure[DataTypeTree]:
        ...

    def get_type_alias_children(self) -> str:
        """Get, in a format manner, a single string with all subtypes found within the generic structure.

        Examples:
            - Union[float, MyDict]
            - Union[float, MyDict, str]
            - MyDict
        """
        child_types = self._get_types()
        return self._format_types(child_types)

    def _format_types(self, child_types: Sequence[str]) -> str:
        """Given a collection of type or type aliases, format them.

        If multiple of them are given, a `Union` type will be used.
        """
        if len(child_types) == 1:
            return child_types[0]
        self.imports.add("Union")
        return f"Union[{', '.join(child_types)}]"

    @final
    def _get_types(self, iterable: Iterable[object] = (), *, remove_repeated: bool = True) -> tuple[str, ...]:
        """
        Get the types of the generic data type tree. Child ones by default.

        This method keeps the order in case the structure used is an ordered one.

        Args:
            iterable (Iterable[object], optional): An iterable of objects. Defaults to an empty iterable.
            remove_repeated (bool, optional): Whether to remove repeated child types. Defaults to True.

        Returns:
            tuple[str, ...]: A tuple containing the child types.
        """
        child_types: list[str] = []
        if iterable:
            child_types = [type(element).__name__ for element in iterable]
        else:
            for child in self:
                if not child.permission_to_be_created_as_type_alias:
                    child_types.append(child.get_str_top_node_without_lvalue())
                else:
                    child_types.append(child.name)
        if not child_types:
            self.imports.add("Any")
            child_types.append("Any")

        if remove_repeated:
            child_types_set = sorted(set(child_types))
            if "float" in child_types and "int" in child_types:
                child_types_set.remove("int")
            return tuple(sorted(child_types_set))
        return tuple(child_types)

    @override
    def _get_hash(self) -> Hashable:
        hashes: list[object] = []
        for child in self:
            hashes.append(child._get_hash())
        return tuple(hashes)
