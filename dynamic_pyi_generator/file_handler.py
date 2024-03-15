import ast
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Final, List, Literal, Tuple, Union

if TYPE_CHECKING:
    from typing_extensions import overload
else:
    overload = lambda x: x  # noqa: E731


class FileHandler:
    lines: List[str]
    tab: Final = "    "

    def __init__(self, representation: str) -> None:
        self.lines = representation.split("\n")

    def __str__(self) -> str:
        return "\n".join(self.lines)

    def __repr__(self) -> str:
        return "\n".join(self.lines)

    @overload
    def search_assignment(
        self, variable: str, only_values: Literal[False] = False
    ) -> List[Tuple[int, str]]: ...

    @overload
    def search_assignment(
        self, variable: str, only_values: Literal[True]
    ) -> List[str]: ...

    def search_assignment(
        self, variable: str, only_values: bool = False
    ) -> Union[List[Tuple[int, str]], List[str]]:
        """
        Searches for assignments of a given variable in the lines of the file.

        Args:
            variable (str): The variable to search for assignments.
            only_values (bool): Only return the values being assigned to that variable.

        Returns:
            List[Tuple[int, str]]: A list of tuples containing the line index and the
                assigned value.
        """
        lst: List[Any] = []
        for idx, line in enumerate(self.lines):
            if variable in line and "=" in line and not self.it_is_string(line, variable):
                value = line.split("=")[-1].strip()
                if isinstance(value, str) and value[0] in ("'", '"'):
                    value = value[1:-1]
                if only_values:
                    lst.append(value)
                else:
                    lst.append((idx, value))
        return lst

    def search_decorator(self, decorator_name: str) -> List[int]:
        lst: List[int] = []
        for idx, line in enumerate(self.lines):
            if "@" in line and f"@{decorator_name}" in line.strip():
                if not self.it_is_string(line, "@"):
                    lst.append(idx)
        return lst

    def search_method(
        self, method_name: str, *, return_index_above_decorator: bool = True
    ) -> List[int]:
        lst: List[int] = []
        for idx, line in enumerate(self.lines):
            if line.strip().startswith(f"def {method_name}") and not self.it_is_string(
                line, method_name
            ):
                if return_index_above_decorator:
                    while "@" in self.lines[idx - 1]:
                        idx = idx - 1
                lst.append(idx)
        return lst

    def it_is_string(self, line: str, keyword_of_interest: str) -> bool:
        for string_symbol in ('"', "'"):
            if string_symbol in line.split(keyword_of_interest)[0]:
                return True
        return False

    def add_line(self, idx: int, line: Union[str, Sequence[str]]) -> None:
        if not isinstance(line, str):
            line = "\n".join(line)
        self.lines.insert(idx, line)

    def search_line(self, keyword: str) -> int:
        for idx, line in enumerate(self.lines):
            if keyword in line:
                return idx
        raise ValueError(f"Line with `{keyword}` could not be found within the file.")

    def replace_line(self, idx: int, line: str) -> None:
        self.lines[idx] = line

    def replace_assignement(self, label: Union[int, str], value: str) -> None:
        if not isinstance(label, int):
            assignment_idx = self.search_assignment(label)
            if not assignment_idx:
                raise ValueError(f"The given label ({label}) is not being assigned.")
            if len(assignment_idx) > 1:
                raise ValueError(
                    f"The given label ({label}) is assigned multiple times. Not clear "
                    "which one should be replaced."
                )
            idx = assignment_idx[0][0]
        else:
            idx = label

        line = self.lines[idx]
        if "=" not in line:
            raise ValueError(f"The given line ({idx}) is not an assignment one.")
        symbols = line.split("=")
        symbols[-1] = value
        self.lines[idx] = "=".join(symbols)

    def remove_all_method_bodies(self) -> None:
        tree = ast.parse(str(self))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                node.body = [ast.Ellipsis()]  # type: ignore
        self.lines = ast.unparse(tree).strip().split("\n")  # type: ignore

    def add_imports(
        self, lines: Union[str, Sequence[str]], *, in_type_checking_block: bool = False
    ) -> None:
        idx = 0
        if isinstance(lines, str):
            lines = [lines]

        if in_type_checking_block:
            idx = self.search_line("if TYPE_CHECKING:") + 1
            lines = [f"{self.tab}{line}" for line in lines]
        for line in lines[::-1]:
            self.lines.insert(idx, line)
