from dataclasses import dataclass, field
from typing import Generic, TypeVar

ObjectT = TypeVar("ObjectT")


@dataclass(frozen=True)
class OrderedSet(Generic[ObjectT]):
    """A data structure that maintains the order of elements while ensuring uniqueness."""

    _elements_added: set[ObjectT] = field(default_factory=set)
    _lst: list[ObjectT] = field(default_factory=list)

    def add(self, element: ObjectT) -> None:
        """
        Adds an element to the ordered set if it is not already present.

        Args:
            element: The element to be added.
        """
        if element not in self._elements_added:
            self._elements_added.add(element)
            self._lst.append(element)

    def as_tuple(self) -> tuple[ObjectT, ...]:
        """
        Returns the elements of the ordered set as a tuple.

        Returns:
            tuple[ObjectT, ...]: The elements of the ordered set as a tuple.
        """
        return tuple(self._lst)

    def as_list(self) -> list[ObjectT]:
        """
        Returns the elements of the ordered set as a list.

        Returns:
            list[ObjectT]: The elements of the ordered set as a list.
        """
        return list(self._lst)
