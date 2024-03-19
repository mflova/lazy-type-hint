from typing import TYPE_CHECKING, Any, Dict, Mapping

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

from dynamic_pyi_generator.parser.parser import ParseOutput, Parser
from dynamic_pyi_generator.utils import TAB, is_string_python_keyword_compatible


class ParserMapping(Parser[Mapping[object, object]]):
    this_one_parses = dict

    @staticmethod
    def _all_keys_are_string(
        data: Mapping[object, object],
    ) -> "TypeGuard[Mapping[str, object]]":
        return all(isinstance(key, str) for key in data)

    @staticmethod
    def _all_keys_are_parsable(data: Mapping[str, object]) -> bool:
        return all(is_string_python_keyword_compatible(key) for key in data)

    def _parse(self, data: Mapping[object, object], *, class_name: str) -> ParseOutput:
        if (
            self._all_keys_are_string(data)
            and self.strategies.mapping_strategy == "TypedDict"
        ):
            if self._all_keys_are_parsable(data):
                string = self._parse_typed_dict(
                    data, class_name=class_name, functional_syntax=False
                )
            else:
                string = self._parse_typed_dict(
                    data, class_name=class_name, functional_syntax=True
                )
        else:
            string = self._parse_dict(data, class_name=class_name)
        return ParseOutput(string, imports=self.imports, to_process=self.to_process)

    def _parse_typed_dict(
        self,
        data: Mapping[str, object],
        *,
        functional_syntax: bool = False,
        class_name: str,
    ) -> str:
        self.imports.add("from typing import TypedDict")

        content: Dict[str, str] = {}
        for key, value in data.items():
            if isinstance(value, dict):
                type_value = f"{class_name}{self.to_camel_case(key)}"
                content[key] = type_value
                self.to_process.append((type_value, value))
            else:
                if type(value) in self.simple_types:
                    content[key] = type(value).__name__
                else:
                    name = f"{class_name}{self.to_camel_case(key)}"
                    self.to_process.append((name, value))
                    content[key] = name
        return self._build_typed_dict(
            name=class_name, content=content, functional_syntax=functional_syntax
        )

    @staticmethod
    def _build_typed_dict(
        name: str, content: Mapping[str, str], *, functional_syntax: bool = False
    ) -> str:
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

    def _parse_dict(self, data: Mapping[object, Any], *, class_name: str) -> str:
        strategy = self.strategies.mapping_strategy
        container = strategy
        if strategy == "TypedDict":
            container = "Dict"
        self.imports.add(f"from typing import {container}")

        keys = self.process_elements(data, class_name=class_name)
        values = self.process_elements(data.values(), class_name=class_name)

        keys_str = self._build_union_elements(keys)
        values_str = self._build_union_elements(values)

        return f"{class_name} = {container}[{keys_str}, {values_str}]"
