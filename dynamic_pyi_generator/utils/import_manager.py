import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Final, List, Literal, Mapping, Optional, Sequence, Set, Tuple

from typing_extensions import TypeGuard

from dynamic_pyi_generator.utils.utils import TAB

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias

KEYWORDS_AVAILABLE: "TypeAlias" = Literal[
    "list",
    "set",
    "tuple",
    "dict",
    "type",
    "Sequence",
    "FrozenSet",
    "Mapping",
    "MappingProxyType",
    "TypedDict",
    "Any",
    "Union",
    "Optional",
    "NotRequired",
    "ReadOnly",
    "Callable",
    "Protocol",
]


@dataclass(frozen=True)
class ImportManager:
    _set: Set[KEYWORDS_AVAILABLE] = field(default_factory=set)

    TEMPLATE: Final[str] = field(init=False, default="from {package} import {name}")
    PACKAGE: Mapping[KEYWORDS_AVAILABLE, Tuple[str, ...]] = field(
        default_factory=lambda: {
            "list": ("typing", "List"),
            "set": ("typing", "Set"),
            "tuple": ("typing", "Tuple"),
            "type": ("typing", "Type"),
            "dict": ("typing", "Dict"),
            "Sequence": ("typing", "Sequence"),
            "FrozenSet": ("typing", "FrozenSet"),
            "Mapping": ("typing", "Mapping"),
            "MappingProxyType": ("types", "MappingProxyType"),
            "TypedDict": ("typing", "TypedDict"),
            "Any": ("typing", "Any"),
            "Union": ("typing", "Union"),
            "Optional": ("typing", "Optional"),
            "NotRequired": ("typing_extensions", "NotRequired"),
            "ReadOnly": ("typing_extensions", "ReadOnly"),
            "Callable": ("typing", "Callable"),
            "Protocol": ("typing", "Protocol"),
        }
    )

    def add(self, keyword: KEYWORDS_AVAILABLE) -> "Self":
        self._set.add(keyword)
        return self

    def import_all_unkown_symbols_from_signature(self, signature: str) -> None:
        """
        Imports all unknown symbols from the given signature.

        Args:
            signature (str): The signature containing type hints.
        """
        hints = re.findall(r":\s*([^\s,]+)", signature)
        for hint in hints:
            hint_ = str(hint).strip().rstrip().replace("):", "")
            self._import_symbols(hint_)

        pattern = r"->\s*([^\s,]+|$)"
        re_output = re.search(pattern, signature)
        return_value: Optional[str] = None
        if re_output:
            return_value = re_output.group(1).rstrip(":")
            self._import_symbols(return_value)

    def _import_symbols(self, symbol: str) -> None:
        """Import all unknown symbols. Including those belonging to generic type hints."""
        symbols = re.findall(r"\b\w+\b", symbol)
        for symbol in symbols:
            symbol = self._cast_symbol(symbol)
            if self._is_importable_symbol(symbol):
                self.add(symbol)

    @staticmethod
    def _cast_symbol(symbol: str) -> str:
        if symbol in ("List", "Tuple", "Set", "Dict"):
            return symbol.lower()
        return symbol

    def _is_importable_symbol(self, symbol: str) -> TypeGuard[KEYWORDS_AVAILABLE]:
        return symbol in self.PACKAGE

    def format(self, *, line_length: int = 90) -> str:
        import_statements: Dict[str, List[str]] = defaultdict(list)
        for keyword in self._set:
            try:
                reference = self.PACKAGE[keyword]
            except KeyError as error:
                raise ValueError(
                    f"The given keyword `{keyword}` could not be located among the available imports: "
                    f"{', '.join(self.PACKAGE.keys())}"
                ) from error
            import_statements[".".join(reference[:-1])].append(reference[-1])

        imports_lst: List[str] = []
        for package, imports in sorted(import_statements.items(), key=lambda x: x[0]):
            imports_lst.append(self._format_single_package(package, imports, line_length=line_length))
        return "\n".join(imports_lst)

    def _format_single_package(self, package: str, imports: Sequence[str], *, line_length: int) -> str:
        string = self.TEMPLATE.format(package=package, name=", ".join(sorted(imports)))
        if len(string) > line_length:
            name = f",\n{TAB}".join(sorted(imports))
            string = self.TEMPLATE.format(package=package, name=f"(\n{TAB}{name}")
            string += ",\n)"
        return string

    def __contains__(self, element: object) -> bool:
        return element in self._set
