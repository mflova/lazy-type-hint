from contextlib import suppress
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    FrozenSet,
    Iterable,
    List,
    Mapping,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

from dynamic_pyi_generator.strategies import Strategies


@dataclass(frozen=True)
class Parser:
    strategies: Strategies
    imports: Set[str] = field(default_factory=set, init=False)
    tab: str = field(default="    ", init=False)

    def parse(self, data: Union[Mapping[str, Any], Sequence[Any]], new_class: str) -> str:
        """
        Parses a dictionary and generates a string representation of a TypedDict class.

        Args:
            data (Mapping[str, Any]): The dictionary to parse.
            new_class (str): The name of the new TypedDict class.

        Returns:
            str: The string representation of the generated TypedDict class.
        """
        header = "from __future__ import annotations\n\n"
        header += "from typing import TypedDict\n"
        typed_dicts_representation = self._parse(data, new_class)
        return header + "\n".join(sorted(self.imports)) + typed_dicts_representation

    def _parse(
        self, data: Union[Mapping[str, Any], Sequence[Any]], new_class: str
    ) -> str:
        if isinstance(data, dict):
            return self._parse_dict(data, new_class=new_class)
        return self._parse_list(data, new_class=new_class)  # type: ignore

    def _parse_list(self, data: Sequence[Mapping[str, Any]], new_class: str) -> str:
        """
        Parses a list of data and generates the corresponding code for a TypedDict.

        If some keys are not present in all elements within the sequence, these would be
        type hinted as `NotRequired`

        Args:
            data (Sequence[Any]): The list of data to be parsed.
            new_class (str): The name of the new class to be created.

        Returns:
            str: The generated code for the TypedDict.

        """
        if self._sequence_contains_same_dicts(data):
            element_type = f"{new_class}Key"
            string = self._parse(data[0], new_class=element_type)
            type_hint_sequence = self._get_type_hint_sequence(
                data, override_element_type=element_type
            )
            string += f"\n\n{new_class} = {type_hint_sequence}"
            return string
        else:  # Create TypedDict with NotRequired keys
            string = f"\n\nclass {new_class}(TypedDict):"
            to_process: List[Tuple[str, Mapping[str, Any]]] = []

            required_keys = self.get_keys_in_common(data)
            not_required_keys = self.get_keys_not_in_common(data)

            for key in required_keys:
                value = data[0][key]
                if not isinstance(value, dict):
                    string += f"\n{self.tab}{key}: {self._get_type_hint(value)}"
                else:
                    class_to_be_created = new_class + key.capitalize()
                    string += f"\n{self.tab}{key}: {class_to_be_created}"
                    to_process.append((class_to_be_created, data[0][key]))

            for key in not_required_keys:
                for element in data:
                    with suppress(KeyError):
                        value = element[key]
                        break

                self.imports.add("from typing_extensions import NotRequired")
                if not isinstance(value, dict):
                    string += (
                        f"\n{self.tab}{key}: NotRequired[{self._get_type_hint(value)}]"
                    )
                else:
                    class_to_be_created = new_class + key.capitalize()
                    string += f"\n{self.tab}{key}: NotRequired[{class_to_be_created}]"
                    to_process.append((class_to_be_created, data[0][key]))
        return string

    def _parse_dict(self, data: Mapping[str, Any], new_class: str) -> str:
        """
        Parses a dictionary and generates a string representation of a TypedDict class.

        Args:
            data (Mapping[str, Any]): The dictionary to be parsed.
            new_class (str): The name of the new TypedDict class to be generated.

        Returns:
            str: A string representation of the generated TypedDict class.
        """
        string = f"\n\nclass {new_class}(TypedDict):"
        to_process: List[Tuple[str, Mapping[str, Any]]] = []

        for key, value in data.items():
            if not isinstance(value, dict):
                string += f"\n{self.tab}{key}: {self._get_type_hint(value)}"
            else:
                class_to_be_created = new_class + key.capitalize()
                string += f"\n{self.tab}{key}: {class_to_be_created}"
                to_process.append((class_to_be_created, data[key]))

        for class_to_be_created, data in to_process:
            string += self._parse(data, class_to_be_created)
        return string

    @staticmethod
    def get_keys_not_in_common(data: Sequence[Mapping[str, Any]]) -> Set[str]:
        """
        Set of keys that are not present in all the dictionaries in the given data.

        Args:
            data (Sequence[Mapping[str, Any]]): A sequence of dictionaries.

        Returns:
            Set[str]: A set of keys that are not present in all the dictionaries.

        """
        keys_in_common = Parser.get_keys_in_common(data)
        output: Set[str] = set()
        for dct in data:
            for key in dct:
                if key not in keys_in_common:
                    output.add(key)
        return output

    @staticmethod
    def get_keys_in_common(data: Sequence[Mapping[str, Any]]) -> Set[str]:
        """
        Returns a set of keys that are common across all mappings in the given data.

        Args:
            data (Sequence[Mapping[str, Any]]): A sequence of mappings.

        Returns:
            Set[str]: A set of keys that are common across all mappings.

        """
        keys = set(data[0].keys())
        for item in data[1:]:
            keys.intersection(item.keys())
        return set(keys)

    @staticmethod
    def _sequence_contains_same_dicts(data: Sequence[Any]) -> bool:
        """
        Check if the given sequence contains only dictionaries with the same keys.

        Args:
            data (Sequence[object]): The sequence to check.

        Returns:
            bool: True if all elements in the sequence are dictionaries with the same
                keys, False otherwise.
        """
        if any(not isinstance(element, dict) for element in data):
            return False
        if not data:
            return False
        data = cast(Sequence[Mapping[str, Any]], data)
        first_element_keys = data[0].keys()
        return all(element.keys() == first_element_keys for element in data[1:])

    def _get_type_hint(self, value: object) -> str:
        """
        Returns the type hint for the given value.

        Args:
            value (object): The value for which to determine the type hint.

        Returns:
            str: The type hint for the given value.
        """
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

    def _get_type_hint_sequence(
        self, value: Sequence[object], *, override_element_type: str = ""
    ) -> str:
        if isinstance(value, list):
            return self._get_type_hint_list(
                value, override_element_type=override_element_type
            )
        if isinstance(value, tuple):
            return self._get_type_hint_tuple(value)
        raise ValueError("Non compatible type was given. Only list or tuple")

    def _get_type_hint_list(
        self, value: List[object], *, override_element_type: str = ""
    ) -> str:
        if self.strategies.list_strategy == "Sequence":
            self.imports.add("from typing import Sequence")
            container = "Sequence[{elements}]"
        else:
            self.imports.add("from typing import List")
            container = "List[{elements}]"

        if self.strategies.list_elements_strategy == "Any":
            self.imports.add("from typing import Any")
            if override_element_type:
                return container.format(elements=override_element_type)
            return container.format(elements="Any")
        elif self.strategies.list_elements_strategy == "object":
            if override_element_type:
                return container.format(elements=override_element_type)
            return container.format(elements="object")
        else:
            types_found = set(map(type, value))
            if len(types_found) == 1:
                if override_element_type:
                    return container.format(elements=override_element_type)
                return container.format(elements=next(iter(types_found)).__name__)
            container = container.format(elements="Union[{elements}]")
            self.imports.add("from typing import Union")
            return container.format(elements=", ".join(self.types_as_str(types_found)))

    def _get_type_hint_tuple(self, value: Tuple[object, ...]) -> str:
        self.imports.add("from typing import Tuple")
        container = "Tuple[{elements}, ...]"
        if self.strategies.tuple_elements_strategy == "Any":
            self.imports.add("from typing import Any")
            return container.format(elements="Any")
        elif self.strategies.tuple_elements_strategy == "object":
            return container.format(elements="object")
        else:
            container = "Tuple[{elements}]"
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
