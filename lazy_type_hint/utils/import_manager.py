import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, Literal, Optional
from collections.abc import Mapping, Sequence

from typing_extensions import TypeGuard

from lazy_type_hint.utils.utils import TAB

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias

KEYWORDS_AVAILABLE: "TypeAlias" = Literal[
    "Sequence",
    "Hashable",
    "Mapping",
    "TypeAlias",
    "MappingProxyType",
    "TypedDict",
    "Any",
    "Union",
    "Optional",
    "NotRequired",
    "ReadOnly",
    "Callable",
    "Protocol",
    "Iterator",
    "Literal",
    "overload",
    "pandas",
    "pd.Scalar",
    "npt",
    "numpy",
    "NDArray",
    "ModuleType",
    "TextIO",
    "annotations",
]


@dataclass(frozen=True)
class ImportManager:
    _set: set[KEYWORDS_AVAILABLE] = field(default_factory=set)

    TEMPLATE: Final[str] = field(init=False, default="from {package} import {name}")
    PACKAGE: Mapping[KEYWORDS_AVAILABLE, tuple[str, ...]] = field(
        default_factory=lambda: {
            "Sequence": ("collections.abc", "Sequence"),
            "Hashable": ("collections.abc", "Hashable"),
            "Mapping": ("collections.abc", "Mapping"),
            "MappingProxyType": ("types", "MappingProxyType"),
            "TypedDict": ("typing", "TypedDict"),
            "Any": ("typing", "Any"),
            "Union": ("typing", "Union"),
            "Optional": ("typing", "Optional"),
            "NotRequired": ("typing_extensions", "NotRequired"),
            "ReadOnly": ("typing_extensions", "ReadOnly"),
            "Callable": ("collections.abc", "Callable"),
            "ModuleType": ("types", "ModuleType"),
            "Protocol": ("typing", "Protocol"),
            "Literal": ("typing", "Literal"),
            "overload": ("typing", "overload"),
            "pandas": ("pandas", "pandas"),
            "npt": ("npt", "npt"),
            "NDArray": ("numpy.typing", "NDArray"),
            "numpy": ("numpy", "numpy"),
            "TypeAlias": ("typing_extensions", "TypeAlias"),
            "pd.Scalar": ("pandas._typing", "Scalar"),
            "TextIO": ("typing", "TextIO"),
            "Iterator": ("collections.abc", "Iterator"),
            "annotations": ("__future__", "annotations"),
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
        import_statements: dict[str, list[str]] = defaultdict(list)
        for keyword in self._set:
            try:
                reference = self.PACKAGE[keyword]
            except KeyError as error:
                raise ValueError(
                    f"The given keyword `{keyword}` could not be located among the available imports: "
                    f"{', '.join(self.PACKAGE.keys())}"
                ) from error
            import_statements[".".join(reference[:-1])].append(reference[-1])

        imports_lst: list[str] = []
        for package, imports in sorted(import_statements.items(), key=lambda x: x[0]):
            imports_lst.append(self._format_single_package(package, imports, line_length=line_length))
        if imports_lst and "__future__" in imports_lst[0]:
            imports_lst[0] += "\n"
        return "\n".join(imports_lst)

    def _format_single_package(self, package: str, imports: Sequence[str], *, line_length: int) -> str:
        if imports[0] == "pandas":
            string = "import pandas as pd"
        elif imports[0] == "npt":
            string = "import numpy.typing as npt"
        elif imports[0] == "numpy":
            string = "import numpy as np"
        else:
            string = self.TEMPLATE.format(package=package, name=", ".join(sorted(imports)))
        if len(string) > line_length:
            name = f",\n{TAB}".join(sorted(imports))
            string = self.TEMPLATE.format(package=package, name=f"(\n{TAB}{name}")
            string += ",\n)"
        return string

    def __contains__(self, element: object) -> bool:
        return element in self._set
