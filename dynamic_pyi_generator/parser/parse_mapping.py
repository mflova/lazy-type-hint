from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

from dynamic_pyi_generator.parser.parser import ParseOutput, Parser


class ParserMapping(Parser[Mapping[object, object]]):
    this_one_parses = dict

    @staticmethod
    def _all_keys_are_string(
        data: Mapping[object, object],
    ) -> "TypeGuard[Mapping[str, object]]":
        return all(isinstance(key, str) for key in data)

    def _parse(self, data: Mapping[object, object], *, class_name: str) -> ParseOutput:
        if (
            self._all_keys_are_string(data)
            and self.strategies.mapping_strategy == "TypedDict"
        ):
            string = self._parse_typed_dict(data, class_name=class_name)
        else:
            string = self._parse_dict(data, class_name=class_name)
        return ParseOutput(string, imports=self.imports, to_process=self.to_process)

    def _parse_typed_dict(self, data: Mapping[str, object], *, class_name: str) -> str:
        self.imports.add("from typing import TypedDict")

        string = f"class {class_name}(TypedDict):\n"
        for key, value in data.items():
            if isinstance(value, dict):
                type_value = f"{class_name}{self.to_camel_case(key)}"
                string += f"{self.tab}{key}: {type_value}\n"
                self.to_process.append((type_value, value))
            else:
                if type(value) in self.simple_types:
                    string += f"{self.tab}{key}: {type(value).__name__}\n"
                else:
                    name = f"{class_name}{self.to_camel_case(key)}"
                    self.to_process.append((name, value))
                    string += f"{self.tab}{key}: {name}\n"
        return string

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
