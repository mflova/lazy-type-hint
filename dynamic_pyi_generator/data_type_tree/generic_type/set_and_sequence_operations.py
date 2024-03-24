"""This module groups common operations that are applied to both sets and sequences.

Although they present a total different behaviour at runtime, from the point of view of type
hinting they are quite similar.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List, Sequence, Set, Tuple, Union

from dynamic_pyi_generator.data_type_tree.factory import data_type_tree_factory

if TYPE_CHECKING:
    from dynamic_pyi_generator.data_type_tree.data_type_tree import DataTypeTree


@dataclass(frozen=True)
class SetAndSequenceOperations:
    data_type_tree: "DataTypeTree"

    def instantiate_childs(self, data: Sequence[Any], *, allow_repeated_childs: bool) -> Tuple["DataTypeTree", ...]:
        """Instantiate the childs for sets and sequences.

        If `allow_repeated_childs` is set to True, all childs will be returned even if they are repeated.
        """
        if allow_repeated_childs:
            childs: Union[Set[DataTypeTree], List[DataTypeTree]] = []
        else:
            childs = set()
        names_added: Set[str] = set()

        for element in data:
            name = f"{self.data_type_tree.name}{type(element).__name__.capitalize()}"
            # Generate new name in case this one was already added
            if name in names_added:
                modified_name = name
                count = 2
                while modified_name in names_added:
                    modified_name = f"{name}{count}"
                    count += 1
                name = modified_name
            child = data_type_tree_factory(
                data=element,
                name=name,
                imports=self.data_type_tree.imports,
                depth=self.data_type_tree.depth + 1,
                parent=self.data_type_tree,
                strategies=self.data_type_tree.strategies,
            )
            if allow_repeated_childs:
                childs.append(child)  # type: ignore
                names_added.add(name)
            else:
                if child not in childs:
                    childs.add(child)  # type: ignore
                    names_added.add(name)
        return tuple(childs)
