from functools import cached_property
from typing import Dict, List, Mapping, NamedTuple, cast

from typing_extensions import TypeGuard, override

from dynamic_pyi_generator.data_type_tree.data_type_tree import DataTypeTree
from dynamic_pyi_generator.data_type_tree.generic_type.mapping_data_type_tree import MappingDataTypeTree
from dynamic_pyi_generator.data_type_tree.simple_data_type_tree import SimpleDataTypeTree
from dynamic_pyi_generator.utils import TAB, is_string_python_keyword_compatible


class DictDataTypeTree(MappingDataTypeTree):
    wraps = dict  # type: ignore

    class DictProfile(NamedTuple):
        """
        Represents the profile of a dictionary data type.

        Attributes:
            is_typed_dict (bool): Indicates whether the dictionary is a TypedDict.
            is_functional_syntax (bool): Indicates whether the dictionary is defined using functional syntax.
        """

        is_typed_dict: bool
        is_functional_syntax: bool

    @staticmethod
    @override
    def _validate_name(name: str) -> None:
        # Removed name validation as the TypedDict can type any name
        return

    @cached_property
    def dict_profile(self) -> DictProfile:
        is_typed_dict = False
        is_functional_syntax = True
        if self._all_keys_are_string(self.childs) and self.strategies.dict_strategy == "TypedDict":
            is_typed_dict = True
            if self._all_keys_are_parsable(self.childs):
                is_functional_syntax = False
        return self.DictProfile(is_typed_dict=is_typed_dict, is_functional_syntax=is_functional_syntax)

    @override
    def _get_str_py(self) -> str:
        if self.dict_profile.is_typed_dict:
            childs_str_key = cast(Mapping[str, DataTypeTree], self.childs)
            if self.dict_profile.is_functional_syntax:
                return self._parse_typed_dict(childs=childs_str_key)
            else:
                return self._parse_typed_dict(childs=childs_str_key)
        else:
            return self._parse_dict(self.childs)

    @staticmethod
    def _all_keys_are_string(data: Mapping[object, DataTypeTree]) -> TypeGuard[Mapping[str, DataTypeTree]]:
        return all(isinstance(key, str) for key in data)

    @staticmethod
    def _all_keys_are_parsable(data: Mapping[str, DataTypeTree]) -> bool:
        return all(is_string_python_keyword_compatible(key) for key in data)

    def _parse_typed_dict(
        self,
        childs: Mapping[str, DataTypeTree],
    ) -> str:
        self.imports.add("from typing import TypedDict")

        content: Dict[str, str] = {}
        for key, value in childs.items():
            if isinstance(value, dict):
                type_value = f"{self.name}{self._to_camel_case(key)}"
                content[key] = type_value
            else:
                if isinstance(value, SimpleDataTypeTree):
                    content[key] = value.holding_type.__name__
                else:
                    name = f"{self.name}{self._to_camel_case(key)}"
                    content[key] = name
        return self._build_typed_dict(
            name=self.name, content=content, functional_syntax=self.dict_profile.is_functional_syntax
        )

    @staticmethod
    def _build_typed_dict(name: str, content: Mapping[str, str], *, functional_syntax: bool = False) -> str:
        """
        Build a typed dictionary based on the given name and content.

        Args:
            name (str): The name of the typed dictionary.
            content (Mapping[str, str]): The content of the typed dictionary, where each
                key-value pair represents a field and its type.
            functional_syntax (bool, optional): If True, use functional syntax to define
                the typed dictionary. Defaults to False.

        Returns:
            str: The string representation of the typed dictionary.

        """
        if functional_syntax:
            template = f"""{name} = TypedDict(
{TAB}"{name}",
{TAB}{{
{TAB}{TAB}"{{key}}": {{value}},
{TAB}}},
)"""
            idx_to_repeat = -3
        else:
            template = f"""class {name}(TypedDict):
{TAB}{{key}}: {{value}}"""
            idx_to_repeat = -1

        lines = template.split("\n")
        modified_line = ""
        for key, value in content.items():
            modified_line += lines[idx_to_repeat].format(key=key, value=value) + "\n"
        lines[idx_to_repeat] = modified_line[:-1]
        return "\n".join(lines)

    @override
    def _get_hash(self) -> object:
        # If TypedDict
        if not self.dict_profile.is_typed_dict:
            return super()._get_hash()
        hashes: List[object] = []
        for name, child in self.childs.items():
            hashes.append(("typed_dict", name, child._get_hash()))
        return frozenset(hashes)
