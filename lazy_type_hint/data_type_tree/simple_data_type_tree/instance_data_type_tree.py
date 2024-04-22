import builtins

from typing_extensions import override

from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import SimpleDataTypeTree


class InstanceDataTypeTree(SimpleDataTypeTree):
    # Change it by `NoneType` once I drop support with Python 3.8
    wraps = (bool, int, float, range, slice, str, type(None))  # + Custom classes

    @override
    def _get_str_top_node(self) -> str:
        if self.holding_type == type(None):
            self.imports.add("TypeAlias")
            self.imports.add("Optional")
            return f"{self.name}: TypeAlias = Optional[object]"

        if self._is_builtin_class():
            if self.parent is None:
                self.imports.add("TypeAlias")
                return f"{self.name}: TypeAlias = {self.holding_type.__name__}"
            else:
                return f"{self.name} = {self.holding_type.__name__}"
        
        if self.parent is None:
            self.imports.add("TypeAlias")
            return f'{self.name}: TypeAlias = "{self.holding_type.__name__}"'
        else:
            return f'{self.name} = "{self.holding_type.__name__}"'

    @override
    def _check_tree_is_correct_one(self, data: object) -> None:
        return

    def _is_builtin_class(self) -> bool:
        try:
            cls = getattr(builtins, self.holding_type.__name__)
            return isinstance(cls, type)
        except AttributeError:
            return False
