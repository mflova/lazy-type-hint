import subprocess
from pathlib import Path
from typing import NamedTuple, Union


class Mypy:
    """
    A class for running the Mypy static type checker.

    Attributes:
        Result: A named tuple representing the result of running Mypy.
    """

    class Result(NamedTuple):
        """Results returned by Mypy."""

        success: bool
        stdout: str

    def run(
        self, file: Union[str, Path], *, strict: bool = False, python_version: str = "3.8"
    ) -> Result:
        """
        Run Mypy on the specified file.

        Args:
            file (Union[str, Path]): The file to run Mypy on.
            strict (bool, optional): Whether to enable strict mode. Defaults to False.
            python_version (str, optional): The Python version to use. Defaults to "3.8".

        Returns:
            Result: The result of running Mypy.

        """
        command = ["mypy"]
        if strict:
            command.append("--strict")
        command.append(f"--python-version {python_version}")
        command.append(str(file))
        result = subprocess.run(" ".join(command), capture_output=True, text=True)
        return self.Result(
            "Success" in result.stdout, result.stdout if result.stdout else result.stderr
        )
