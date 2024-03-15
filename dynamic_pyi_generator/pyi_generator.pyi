import os
import shutil
from collections.abc import Mapping
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal, Union, final, overload

import yaml

from dynamic_pyi_generator.typed_dict_generator import parse

if TYPE_CHECKING:
    from .build.Person import Person
    from typing_extensions import TypeAlias

THIS_DIR = Path(__file__).parent


class PyiGeneratorError(Exception):
    ...


class PyiGenerator:
    loader_pyi: str
    loader_pyi_path: Path
    classes_created: "TypeAlias" = Union[Literal["Person"], Any]
    custom_class_dir: Final = "build"
    tab: Final = "    "

    @final
    def __init__(self) -> None:
        self.loader_pyi_path = Path(__file__).with_suffix(".pyi")
        if not self.loader_pyi_path.exists():
            self.loaded_pyi_content = self.generate_loader_pyi()
        else:
            self.loaded_pyi_content = self.loader_pyi_path.read_text(encoding="utf-8")

    def get_classes_added(self) -> set[str]:
        to_find = "classes_created"
        for line in self.loaded_pyi_content.split("\n"):
            if "classes_created" in line:
                break
        else:
            raise PyiGeneratorError(f"No `{to_find}` was found in this file.")

        value = line.split("=")[-1].strip()
        if value == "Any":
            return set()
        else:
            pattern = r'"(.*?)"'
            matches = re.findall(pattern, value)
            return set(matches)

    @staticmethod
    def _find_line_idx(string: str,*, keyword: str) -> int:
        for idx, line in enumerate(string.split("\n")):
            if keyword in line:
                return idx
        raise PyiGeneratorError(f"It was not possible to find {keyword} among the lines of the given string.")

    @overload
    def load(self, dct: Mapping[str, Any], class_type: Literal["Person"]) -> Person:
        ...

    @overload
    def load(self, dct: Mapping[str, Any], class_type: str) -> Any:
        if class_type not in self.get_classes_added():
            string = parse(dct, new_class=class_type)
            self.create_custom_class_pyi(string, class_type)
            self.add_new_class_to_loader_pyi(class_type)
        return dct

    def reset(self) -> None:
        self.reset_custom_class_pyi()
        self.reset_loader_pyi()

    @final
    def generate_loader_pyi(self) -> str:
        content = Path(__file__).read_text()
        
        # Prepend @overload decorator to load function
        idx = self._find_line_idx(content, keyword="def load(")
        lines = content.split("\n")
        
        lines.insert(idx, f"{self.tab}@overload")
        return "\n".join(lines)

    def create_custom_class_pyi(self, string: str, class_name: str) -> None:
        custom_class_dir = Path(__file__).parent / self.custom_class_dir
        if not custom_class_dir.exists():
            os.makedirs(custom_class_dir)

        path = custom_class_dir / f"{class_name}.pyi"
        path.write_text(string)

    @final
    def add_new_class_to_loader_pyi(self, new_class: str) -> None:
        self._add_class_created_to_loader_pyi(new_class)
        self._add_import_to_loader_pyi(new_class)
        self._add_overload_to_loader_pyi(new_class)

    @final
    def reset_loader_pyi(self) -> None:
        self.loaded_pyi_content = self.generate_loader_pyi()
        self.update_loader_pyi()

    @final
    def reset_custom_class_pyi(self) -> None:
        path = Path(__file__).parent / self.custom_class_dir
        if path.exists():
            shutil.rmtree(path)

    @final
    def _add_import_to_loader_pyi(self, new_class: str) -> None:
        lines = self.loaded_pyi_content.split("\n")
        idx = self._find_line_idx(self.loaded_pyi_content, keyword="if TYPE_CHECKING")
        lines.insert(idx + 1, f"{self.tab}from .build.{new_class} import {new_class}")
        self.loaded_pyi_content = "\n".join(lines)
        self.update_loader_pyi()

    @final
    def _add_overload_to_loader_pyi(self, new_class: str) -> None:
        string = f"""{self.tab}@overload\n{self.tab}def load(self, dct: Mapping[str, Any], class_type: Literal["{new_class}"]) -> {new_class}:\n{self.tab*2}...\n"""

        lines = self.loaded_pyi_content.split("\n")
        # If there are not any overloads:
        if f"@overload\n{self.tab}def load" in self.loaded_pyi_content:
            line_found = -1
            line_found = self._find_line_idx(self.loaded_pyi_content, keyword="@overload")

        # If there are existing overloads:
        else:
            line_found = self._find_line_idx(self.loaded_pyi_content, keyword="def load(") - 1
        lines.insert(line_found, string)
        self.loaded_pyi_content = "\n".join(lines)
        self.update_loader_pyi()

    @final
    def _add_class_created_to_loader_pyi(self, new_class: str) -> None:
        to_find = "classes_created"
        lines = self.loaded_pyi_content.split("\n")

        for idx, line in enumerate(lines):
            if to_find in line:
                value = line.split("=")[1].strip()
                idx_line_found = idx
                break
        else:
            raise PyiGeneratorError(f"No `{to_find}` was found in this file.")

        # Case: Any
        if value == "Any":
            value = f'Union[Literal["{new_class}"], Any]'
        # Case: Union[Literal["A"], Any]
        else:
            value = value.replace("], Any]", f', "{new_class}"], Any]')

        new_line = lines[idx_line_found].split("=")
        new_line[-1] = f"= {value}"

        new_line = "".join(new_line)
        lines[idx] = new_line
        self.loaded_pyi_content = "\n".join(lines)
        self.update_loader_pyi()

    @final
    def update_loader_pyi(self) -> None:
        self.loader_pyi_path.write_text(self.loaded_pyi_content)