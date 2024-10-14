import ast
import inspect
import textwrap
from inspect import Parameter
from types import BuiltinFunctionType, FunctionType, MappingProxyType, MethodType
from typing import Any, Callable, Optional
from collections.abc import Hashable

from typing_extensions import override

from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import SimpleDataTypeTree
from lazy_type_hint.utils import TAB


class FunctionDataTypeTree(SimpleDataTypeTree):
    wraps = (FunctionType, staticmethod, classmethod, BuiltinFunctionType, MethodType)
    data: Callable[[Any], Any]

    @property
    def is_lambda(self) -> bool:
        return bool(self.data.__name__ == "<lambda>")

    @override
    @property
    def permission_to_be_created_as_type_alias(self) -> bool:
        if self.is_lambda or self.parent is None:
            return True
        return True

    @property
    def can_be_inspected(self) -> bool:
        try:
            inspect.signature(self.data)
            return True
        except ValueError:
            return False

    def _get_str_top_node(self) -> str:
        if not self.can_be_inspected:
            self.imports.add("Callable").add("TypeAlias")
            return f"{self.name}: TypeAlias = Callable"
        if self.is_lambda:
            return self._get_lambda_str()
        return self._get_protocol_str()

    def _get_protocol_str(self) -> str:
        args = str(inspect.signature(self.data)).replace("collections.abc.", "")
        self.imports.add("Protocol")
        self.imports.import_all_unkown_symbols_from_signature(args)

        if "->" not in args:
            if not self._has_return():
                return f"""class {self.name}(Protocol):\n{TAB}def __call__{args} -> None: ..."""
            self.imports.add("Any")
            return f"""class {self.name}(Protocol):\n{TAB}def __call__{args} -> Any: ..."""
        return f"""class {self.name}(Protocol):\n{TAB}def __call__{args}: ..."""

    def get_func_params(self) -> MappingProxyType[str, Parameter]:
        signature = inspect.signature(self.data)
        return signature.parameters

    def _get_lambda_str(self) -> str:
        self.imports.add("Callable").add("Any").add("TypeAlias")
        if self.can_be_inspected:
            return (
                f"{self.name}: TypeAlias = Callable[[{', '.join(['Any']*len(self.get_func_params().values()))}], Any]"
            )
        return f"{self.name}: TypeAlias = Callable"

    @override
    def _get_hash(self) -> Hashable:
        if self.is_lambda and self.can_be_inspected:
            return str(f"Callable[[{', '.join(['Any']*len(self.get_func_params().values()))}], Any]")
        else:
            if self.can_be_inspected:
                return str(inspect.signature(self.data))
            return "Callable"

    def _has_return(self) -> Optional[bool]:
        code = textwrap.dedent(inspect.getsource(self.data))
        try:
            tree = ast.parse(code)
        except:  # noqa: E722
            return None
        return any(isinstance(node, ast.Return) for node in ast.walk(tree))
