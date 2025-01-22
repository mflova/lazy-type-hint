import re
import subprocess
from pathlib import Path
from typing import Final

DOCS_ROOT: Final = Path(__file__).parent.parent / "docs"

def test_docs_are_building() -> None:
    status = subprocess.run(["poetry", "run", "mkdocs", "build", "--clean", "--strict"], check=False).returncode
    assert status == 0, "Docs are not building"


def test_python_blocks_are_ok(tmp_path: Path) -> None:
    """Verify that all Python code blocks in the docs are correct from type-checking point of view."""
    temp_file = tmp_path / "file.py"
    for file in DOCS_ROOT.rglob("*.md"):
        content = file.read_text(encoding="utf-8")

        code_blocks = re.findall(r"```(?:python|py)\n(.*?)```", content, re.DOTALL)

        if code_blocks:
            with open(temp_file, "a") as out:
                for block in code_blocks:
                    out.write(block + "\n\n")

    returncode = subprocess.run(["poetry", "run", "mypy", str(temp_file)]).returncode
    assert returncode == 0, (
        "There were errors reported by Mypy in at least one markdown file with a Python code snippet."
    )


def test_strategies_are_documented() -> None:
    raise NotImplementedError