import builtins

from typing_extensions import override

from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import SimpleDataTypeTree


class TypeDataTypeTree(SimpleDataTypeTree):
    wraps = (type,)
    data: type[object]

    @override
    def _get_str_top_node(self) -> str:
        self.imports.add("TypeAlias")
        if self.is_builtin_class():
            return f"{self.name}: TypeAlias = type[{self.data.__name__}]"
        return f'{self.name}: TypeAlias = type["{self.data.__name__}"]'

    def is_builtin_class(self) -> bool:
        try:
            cls = getattr(builtins, self.data.__name__)
            return isinstance(cls, type)
        except AttributeError:
            return False
