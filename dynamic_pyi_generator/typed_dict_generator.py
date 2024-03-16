from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    FrozenSet,
    Iterable,
    List,
    Literal,
    Set,
    Tuple,
    Type,
    Union,
)


@dataclass(frozen=True)
class Parser:
    type_hint_lists_as_sequences: bool = False
    type_hint_strategy_for_list_elements: Literal["Any", "object", "Union"] = "Union"
    type_hint_strategy_for_tuple_elements: Literal[
        "Any", "object", "fix size"
    ] = "fix size"
    imports: Set[str] = field(default_factory=set, init=False)

    def parse(self, dct: Mapping[str, Any], new_class: str) -> str:
        """
        Parses a dictionary and generates a string representation of a TypedDict class.

        Args:
            dct (Mapping[str, Any]): The dictionary to parse.
            new_class (str): The name of the new TypedDict class.

        Returns:
            str: The string representation of the generated TypedDict class.
        """
        header = "from __future__ import annotations\n\n"
        header += "from typing import TypedDict\n"
        typed_dicts_representation = self._parse(dct, new_class)
        return header + "\n".join(sorted(self.imports)) + typed_dicts_representation

    def _parse(self, dct: Mapping[str, Any], new_class: str) -> str:
        tab = "    "
        string = f"\n\nclass {new_class}(TypedDict):"
        to_process: List[Tuple[str, Mapping[str, Any]]] = []

        for key, value in dct.items():
            if not isinstance(value, dict):
                string += f"\n{tab}{key}: {self._get_type_hint(value)}"
            else:
                class_to_be_created = new_class + key.capitalize()
                string += f"\n{tab}{key}: {class_to_be_created}"
                to_process.append((class_to_be_created, dct[key]))

        for class_to_be_created, dct in to_process:
            string += self._parse(dct, class_to_be_created)
        return string

    def _get_type_hint(self, value: object) -> str:
        functions: Mapping[object, Callable[[Any], str]] = {
            list: self._get_type_hint_list,
            tuple: self._get_type_hint_tuple,
            int: self._get_type_hint_number,
            float: self._get_type_hint_number,
            str: self._get_type_hint_str,
            set: self._get_type_hint_set,
            frozenset: self._get_type_hint_set,
        }
        return functions[type(value)](value)

    def _get_type_hint_list(self, value: List[object]) -> str:
        if self.type_hint_lists_as_sequences:
            self.imports.add("from typing import Sequence")
            container = "Sequence[{elements}]"
        else:
            self.imports.add("from typing import List")
            container = "List[{elements}]"

        if self.type_hint_strategy_for_list_elements == "Any":
            self.imports.add("from typing import Any")
            return container.format(elements="Any")
        elif self.type_hint_strategy_for_list_elements == "object":
            return container.format(elements="object")
        else:
            types_found = set(map(type, value))
            if len(types_found) == 1:
                return container.format(elements=next(iter(types_found)).__name__)
            container = container.format(elements="Union[{elements}]")
            self.imports.add("from typing import Union")
            return container.format(elements=", ".join(self.types_as_str(types_found)))

    def _get_type_hint_tuple(self, value: Tuple[object, ...]) -> str:
        self.imports.add("from typing import Tuple")
        container = "Tuple[{elements}]"
        if self.type_hint_strategy_for_tuple_elements == "Any":
            self.imports.add("from typing import Any")
            return container.format(elements="Any")
        elif self.type_hint_strategy_for_tuple_elements == "object":
            return container.format(elements="object")
        else:
            types_found = tuple(map(type, value))
            if len(types_found) == 1:
                return container.format(elements=next(iter(types_found)).__name__)
            return container.format(elements=", ".join(self.types_as_str(types_found)))

    def _get_type_hint_number(self, value: float) -> str:
        return type(value).__name__

    def _get_type_hint_str(self, value: str) -> str:
        return type(value).__name__

    def _get_type_hint_set(self, value: Union[Set[object], FrozenSet[object]]) -> str:
        types_found = set(map(type, value))
        if isinstance(value, set):
            container = "Set[{elements}]"
            self.imports.add("from typing import Set")
        else:
            container = "FrozenSet[{elements}]"
            self.imports.add("from typing import FrozenSet")

        if len(types_found) == 1:
            return container.format(elements=next(iter(types_found)).__name__)
        return container.format(elements=", ".join(self.types_as_str(types_found)))

    @staticmethod
    def types_as_str(types: Iterable[Type[object]]) -> List[str]:
        return [value.__name__ for value in types]
