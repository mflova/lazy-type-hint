from abc import abstractmethod
from typing import (
    Any,
    Hashable,
    Iterable,
    Iterator,
    List,
    Mapping,
    Sequence,
    Set,
    Tuple,
    Union,
    final,
)

from typing_extensions import Self, override

from dynamic_pyi_generator.data_type_tree.data_type_tree import ChildStructure, DataTypeTree
from dynamic_pyi_generator.data_type_tree.simple_data_type_tree import SimpleDataTypeTree


class GenericDataTypeTree(DataTypeTree):
    childs: ChildStructure[DataTypeTree]

    # Iterable-protocol related
    _iterator: Union[int, Iterator[Hashable]]

    @abstractmethod
    def _get_childs(self, data: object) -> ChildStructure[DataTypeTree]:
        ...

    def get_type_alias_childs(self) -> str:
        child_types = self._get_types()
        return self._format_types(child_types)

    def _format_types(self, child_types: Sequence[str]) -> str:
        if len(child_types) == 1:
            return child_types[0]
        self.imports.add("from typing import Union")
        return f"Union[{', '.join(child_types)}]"

    @final
    def _get_types(self, iterable: Iterable[object] = (), *, remove_repeated: bool = True) -> Tuple[str, ...]:
        """
        Get the types of the generic data type tree. Child ones by default.

        This method keeps the order in case the structure used is an ordered one.

        Args:
            iterable (Iterable[object], optional): An iterable of objects. Defaults to an empty iterable.
            remove_repeated (bool, optional): Whether to remove repeated child types. Defaults to True.

        Returns:
            Tuple[str, ...]: A tuple containing the child types.

        """
        child_types: List[str] = []
        if iterable:
            child_types = [type(element).__name__ for element in iterable]
        else:
            for child in self:
                if isinstance(child, SimpleDataTypeTree):
                    child_types.append(child.holding_type.__name__)
                else:
                    child_types.append(child.name)
        if not child_types:
            self.imports.add("from typing import Any")
            child_types.append("Any")

        if remove_repeated:
            child_types_set = sorted(set(child_types))
            if "float" in child_types and "int" in child_types:
                child_types_set.remove("int")
            return tuple(sorted(child_types_set))
        return tuple(child_types)

    def __iter__(self) -> Self:
        if isinstance(self.childs, Mapping):
            self._iterator = iter(self.childs.keys())
        else:
            self._iterator = 0  # Reset the index to zero when starting a new iteration
        return self

    def __next__(self) -> DataTypeTree:
        # Many type ignores here but everything is safe
        if isinstance(self.childs, Mapping):
            key = next(self._iterator, None)  # type: ignore
            if key is not None:
                return self.childs[key]
            else:
                raise StopIteration
        else:
            if self._iterator < len(self.childs):  # type: ignore
                element = list(self.childs)[self._iterator]  # type: ignore
                self._iterator += 1  # type: ignore
                return element
            else:
                raise StopIteration

    @override
    def _get_hash(self) -> object:
        hashes: List[object] = []
        for child in self:
            hashes.append(child._get_hash())
        return tuple(hashes)


def get_childs_for_set_and_sequence(
    self: DataTypeTree, data: Sequence[Any], *, allow_repeated_childs: bool
) -> Tuple[DataTypeTree, ...]:
    if allow_repeated_childs:
        childs: Union[Set[DataTypeTree], List[DataTypeTree]] = []
    else:
        childs = set()
    names_added: Set[str] = set()

    for element in data:
        data_type_tree = self.get_data_type_tree_for_type(type(element))
        name = f"{self.name}{type(element).__name__.capitalize()}"
        # Generate new name in case this one was already added
        if name in names_added:
            modified_name = name
            count = 2
            while modified_name in names_added:
                modified_name = f"{name}{count}"
                count += 1
            name = modified_name
        child = data_type_tree(
            data=element,
            name=name,
            simplify_redundant_types=self.simplify_redundant_types,
            imports=self.imports,
            depth=self.depth + 1,
            parent=self,
            strategies=self.strategies,
        )
        if allow_repeated_childs:
            childs.append(child)  # type: ignore
            names_added.add(name)
        else:
            if child not in childs:
                childs.add(child)  # type: ignore
                names_added.add(name)
    return tuple(childs)
