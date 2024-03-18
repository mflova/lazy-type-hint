from dynamic_pyi_generator.parser.parser import ParseOutput, Parser


class ParserStr(Parser[str]):
    this_one_parses = str

    def _parse(self, data: str, *, class_name: str) -> ParseOutput:  # noqa: ARG002
        return ParseOutput(
            f"\n\n{class_name} = str", imports=self.imports, to_process=self.to_process
        )
