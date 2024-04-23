import io

from typing_extensions import override

from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import SimpleDataTypeTree


class IoDataTypeTree(SimpleDataTypeTree):
    wraps = (io.IOBase,)

    @override
    def _get_str_top_node(self) -> str:
        self.imports.add("TextIO").add("TypeAlias")
        return f"{self.name}: TypeAlias = TextIO"
