import builtins
from typing import Type

from typing_extensions import override

from dynamic_pyi_generator.data_type_tree.simple_data_type_tree.simple_data_type_tree import SimpleDataTypeTree


class TypeDataTypeTree(SimpleDataTypeTree):
    wraps = type
    data: Type[object]

    @override
    def _get_str_top_node(self) -> str:
        self.imports.add("type")
        if self.is_builtin_class():
            return f"{self.name} = Type[{self.data.__name__}]"
        return f'{self.name} = Type["{self.data.__name__}"]'

    def is_builtin_class(self) -> bool:
        try:
            cls = getattr(builtins, self.data.__name__)
            return isinstance(cls, type)
        except AttributeError:
            return False
