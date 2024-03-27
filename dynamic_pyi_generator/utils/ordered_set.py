import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generic, Iterable, List, NamedTuple, Set, Tuple, TypeVar, Union

from dynamic_pyi_generator.utils.utils import check_if_command_available

ObjectT = TypeVar("ObjectT")


@dataclass(frozen=True)
class OrderedSet(Generic[ObjectT]):
    """A data structure that maintains the order of elements while ensuring uniqueness."""

    _elements_added: Set[ObjectT] = field(default_factory=set)
    _lst: List[ObjectT] = field(default_factory=list)

    def add(self, element: ObjectT) -> None:
        """
        Adds an element to the ordered set if it is not already present.

        Args:
            element: The element to be added.
        """
        if element not in self._elements_added:
            self._elements_added.add(element)
            self._lst.append(element)

    def as_tuple(self) -> Tuple[ObjectT, ...]:
        """
        Returns the elements of the ordered set as a tuple.

        Returns:
            Tuple[ObjectT, ...]: The elements of the ordered set as a tuple.
        """
        return tuple(self._lst)

    def as_list(self) -> List[ObjectT]:
        """
        Returns the elements of the ordered set as a list.

        Returns:
            List[ObjectT]: The elements of the ordered set as a list.
        """
        return list(self._lst)
