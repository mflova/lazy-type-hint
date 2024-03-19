from dynamic_pyi_generator.parser.parser import ParseOutput, Parser


class ParserBool(Parser[bool]):
    this_one_parses = bool

    def _parse(self, data: bool, *, class_name: str) -> ParseOutput:  # noqa: ARG002
        return ParseOutput(
            f"{class_name} = bool", imports=self.imports, to_process=self.to_process
        )
