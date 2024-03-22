from typing import Union, final

from typing_extensions import Self, override

from dynamic_pyi_generator.data_type_tree.data_type_tree import DataTypeTree


class SimpleDataTypeTree(DataTypeTree):
    childs: None
    wraps = (bool, int, float, range, slice, str, type(None))

    @override
    def _get_childs(self, data: Union[bool, float, str]) -> None:  # type: ignore
        return None

    @override
    def _get_str_py(self) -> str:
        return f"{self.name} = {self.holding_type.__name__}"

    @final
    def __iter__(self) -> Self:
        return self

    @final
    def __next__(self) -> DataTypeTree:
        raise StopIteration

    @override
    def _get_hash(self) -> int:
        return id(self.holding_type)
