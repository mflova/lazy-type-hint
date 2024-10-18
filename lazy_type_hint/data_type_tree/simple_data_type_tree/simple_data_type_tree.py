from typing import Union, final
from collections.abc import Hashable

from typing_extensions import Self, override

from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree


class SimpleDataTypeTree(DataTypeTree):
    """Tree that holds any kind of object that cannot contain inner structures (children)."""

    children: None

    @final
    @override
    def _instantiate_children(self, data: Union[bool, float, str]) -> None:  # type: ignore
        return None

    @final
    @override
    def __iter__(self) -> "Self":
        return self

    @final
    @override
    def __next__(self) -> DataTypeTree:
        raise StopIteration

    @override
    def _get_hash(self) -> Hashable:
        return id(self.holding_type)

    @final
    @override
    def _get_height(self) -> int:
        return 0

    @override
    @property
    def permission_to_be_created_as_type_alias(self) -> bool:
        if self.parent is None:
            return True
        return False
