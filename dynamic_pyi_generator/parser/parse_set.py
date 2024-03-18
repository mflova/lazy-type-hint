from typing import Any, FrozenSet, Literal, Set, Union

from dynamic_pyi_generator.parser.parser import ParseOutput, Parser


class ParserSet(Parser[Union[Set[Any], FrozenSet[Any]]]):
    this_one_parses = (set, frozenset)

    def _parse(
        self, data: Union[Set[Any], FrozenSet[Any]], *, class_name: str
    ) -> ParseOutput:
        string = ""
        if isinstance(data, set):
            string = self._parse_set(data, class_name=class_name, container_name="Set")
        if isinstance(data, frozenset):
            string = self._parse_set(
                data, class_name=class_name, container_name="FrozenSet"
            )
        return ParseOutput(string, imports=self.imports, to_process=self.to_process)

    def _parse_set(
        self,
        data: Union[Set[Any], FrozenSet[Any]],
        *,
        class_name: str,
        container_name: Literal["Set", "FrozenSet"],
    ) -> str:
        self.imports.add(f"from typing import {container_name}")

        strategy = self.strategies.set_elements_strategy
        if strategy == "Any" or strategy == "object":
            if strategy == "Any":
                self.imports.add("from typing import Any")
            return f"{class_name} = {container_name}[{strategy}]"

        subtypes = self.process_elements(data, class_name=class_name)
        return f"{class_name} = {container_name}[{self._build_union_elements(subtypes)}]"
