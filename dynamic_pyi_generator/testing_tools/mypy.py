import subprocess
from pathlib import Path
from typing import Iterable, List, NamedTuple, Union


class Mypy:
    """
    A class for running the Mypy static type checker.

    Attributes:
        Result: A named tuple representing the result of running Mypy.
    """

    class Result(NamedTuple):
        """Results returned by Mypy."""

        success: bool
        errors: List[str]

        def errors_as_str(self) -> str:
            return "\n".join(self.errors)

    def run(
        self,
        file: Union[str, Path],
        *,
        strict: bool = False,
        python_version: str = "3.8",
        ignore_errors: Iterable[str] = (),
    ) -> Result:
        """
        Run Mypy on the specified file.

        Args:
            file (Union[str, Path]): The file to run Mypy on.
            strict (bool, optional): Whether to enable strict mode. Defaults to False.
            python_version (str, optional): The Python version to use. Defaults to "3.8".
            ignore_errors (Iterable[str], optional): A collection of error strings to
                ignore. Defaults to ().

        Returns:
            Result: The result of running Mypy.

        """
        command = ["mypy"]
        if strict:
            command.append("--strict")
        command.append(f"--python-version {python_version}")
        command.append(str(file))
        result = subprocess.run(" ".join(command), capture_output=True, text=True)

        if result.stderr:
            raise ValueError(f"Mypy could not run: {result.stderr}")

        error_lst = [line for line in result.stdout.split("\n") if "error: " in line]
        error_lst = [
            line
            for line in error_lst
            if not all(ignore_error in line for ignore_error in ignore_errors)
        ]
        return self.Result(
            success=not bool(error_lst),
            errors=error_lst,
        )
