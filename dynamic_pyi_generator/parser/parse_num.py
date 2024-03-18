from dynamic_pyi_generator.parser.parser import ParseOutput, Parser


class ParserNum(Parser[float]):
    this_one_parses = (int, float)

    def _parse(self, data: float, *, class_name: str) -> ParseOutput:  # noqa: ARG002
        return ParseOutput(
            f"\n\n{class_name} = str", imports=self.imports, to_process=self.to_process
        )
