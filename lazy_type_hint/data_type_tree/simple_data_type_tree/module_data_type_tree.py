from types import ModuleType

from typing_extensions import override

from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import SimpleDataTypeTree


class ModuleTypeDataTypeTree(SimpleDataTypeTree):
    wraps = ModuleType

    @override
    def _get_str_top_node(self) -> str:
        self.imports.add("ModuleType")
        return f"{self.name} = ModuleType"
