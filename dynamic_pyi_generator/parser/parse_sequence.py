from typing import Any, Literal, Sequence, Tuple

from dynamic_pyi_generator.parser.parser import ParseOutput, Parser, ParserError


class ParserSequence(Parser[Sequence[Any]]):
    this_one_parses = (list, tuple)

    def _parse(self, data: Sequence[Any], *, class_name: str) -> ParseOutput:
        string = ""
        if isinstance(data, list):
            if self.strategies.list_strategy == "Sequence":
                string = self._parse_sequence(
                    data, class_name=class_name, container_name="Sequence"
                )
            elif self.strategies.list_strategy == "list":
                string = self._parse_sequence(
                    data, class_name=class_name, container_name="List"
                )
        if isinstance(data, tuple):
            string = self._parse_sequence(
                data, class_name=class_name, container_name="Tuple"
            )
        return ParseOutput(string, imports=self.imports, to_process=self.to_process)

    def _parse_sequence(
        self,
        data: Sequence[Any],
        *,
        class_name: str,
        container_name: Literal["Tuple", "List", "Sequence"],
    ) -> str:
        if isinstance(data, tuple):
            return self._parse_tuple(data, class_name=class_name)

        self.imports.add(f"from typing import {container_name}")

        strategy = self.strategies.sequence_elements_strategy
        if strategy == "Any" or strategy == "object":
            if strategy == "Any":
                self.imports.add("from typing import Any")
            return f"{class_name} = {container_name}[{strategy}]"

        subtypes = self.process_elements(data, class_name=class_name)
        return f"{class_name} = {container_name}[{self._build_union_elements(subtypes)}]"

    def _parse_tuple(
        self,
        data: Tuple[Any, ...],
        *,
        class_name: str,
    ) -> str:
        self.imports.add("from typing import Tuple")
        strategy_size = self.strategies.tuple_size_strategy
        strategy_elements = self.strategies.tuple_elements_strategy
        if strategy_size == "...":
            subtypes = self.process_elements(
                data, class_name=class_name, include_repeated=False
            )
            if strategy_elements == "Any":
                self.imports.add("from typing import Any")
                return f"{class_name} = Tuple[Any, ...]"
            if strategy_elements == "object":
                return f"{class_name} = Tuple[object, ...]"
            if strategy_elements == "Union":
                if len(subtypes) == 1:
                    return f"{class_name} = Tuple[{next(iter(subtypes))}, ...]"
                self.imports.add("from typing import Union")
                return f"{class_name} = Tuple[Union[{', '.join(subtypes)}], ...]"
        if strategy_size == "fixed":
            subtypes_lst = self.process_elements(
                data, class_name=class_name, include_repeated=True
            )
            if strategy_elements == "Any":
                self.imports.add("from typing import Any")
                any_ = ["Any"] * len(subtypes_lst)
                return f"{class_name} = Tuple[{', '.join(any_)}]"
            if strategy_elements == "object":
                object_ = ["object"] * len(subtypes_lst)
                return f"{class_name} = Tuple[{', '.join(object_)}]"
            if strategy_elements == "Union":
                return f"{class_name} = Tuple[{', '.join(subtypes_lst)}]"
        raise ParserError(
            "Combination of strategies chosen are not available: "
            f"{strategy_elements} and {strategy_elements}"
        )
