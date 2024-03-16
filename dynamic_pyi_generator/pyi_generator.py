import importlib
import os
import re
import shutil
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Literal,
    Set,
    TypeVar,
    Union,  # noqa: F401
    final,
    overload,  # noqa: F401
)

import dynamic_pyi_generator
from dynamic_pyi_generator.file_handler import FileHandler
from dynamic_pyi_generator.typed_dict_generator import Parser
from dynamic_pyi_generator.typed_dict_validator import validate_dict

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

THIS_DIR = Path(__file__).parent


class PyiGeneratorError(Exception):
    ...


MappingT = TypeVar("MappingT", bound=dict)


class PyiGenerator:
    this_file_pyi: FileHandler
    """.pyi representation of this same module."""
    this_file_pyi_path: Path
    """Path to the .pyi file associated to this same module."""
    classes_created: "TypeAlias" = Any
    """Classes created by the class. Do not modify."""
    custom_class_dir: Final = "build"
    """Name of the direcotry that will contain all the generated stubs."""
    tab: Final = "    "
    """Tabs used whenever an indent is needed."""

    @final
    def __init__(self) -> None:
        self.this_file_pyi_path = Path(__file__).with_suffix(".pyi")
        if not self.this_file_pyi_path.exists():
            self.this_file_pyi = self.generate_this_file_pyi()
        else:
            self.this_file_pyi = FileHandler(
                self.this_file_pyi_path.read_text(encoding="utf-8")
            )

    def get_classes_added(self) -> Set[str]:
        to_find = "classes_created"
        values = self.this_file_pyi.search_assignment("classes_created", only_values=True)
        if not values:
            raise PyiGeneratorError(f"No `{to_find}` was found in this file.")

        if values[0] == "Any":
            return set()
        matches = re.findall(r'"(.*?)"', values[0])
        return set(matches)

    @staticmethod
    def _find_line_idx(string: str, *, keyword: str) -> int:
        for idx, line in enumerate(string.split("\n")):
            if keyword in line:
                return idx
        raise PyiGeneratorError(
            f"It was not possible to find {keyword} among the lines of the given string."
        )

    @classmethod
    def from_dct(
        cls,
        dct: MappingT,
        class_type: str,
        *,
        type_hint_lists_as_sequences: bool = False,
        type_hint_strategy_for_list_elements: Literal["Any", "object", "Union"] = "Union",
        type_hint_strategy_for_tuple_elements: Literal[
            "Any", "object", "fix size"
        ] = "fix size",
    ) -> MappingT:
        self = cls()
        if class_type not in self.get_classes_added():
            typed_dict_representation = Parser(
                type_hint_lists_as_sequences=type_hint_lists_as_sequences,
                type_hint_strategy_for_list_elements=type_hint_strategy_for_list_elements,
                type_hint_strategy_for_tuple_elements=type_hint_strategy_for_tuple_elements,
            ).parse(dct, new_class=class_type)
            self.create_custom_class_pyi(typed_dict_representation, class_type)
            self.add_new_class_to_loader_pyi(
                new_class=class_type, method_name=self.from_dct.__name__
            )
        else:
            module = importlib.import_module(
                f"{dynamic_pyi_generator.__name__}.{self.custom_class_dir}.{class_type}"
            )
            typed_dict_class = getattr(module, class_type)
            if not validate_dict(dct, typed_dict_class):
                raise PyiGeneratorError(
                    f"An attempt to load a dictionary with an already existing class "
                    f"type ({class_type}) has been made. However, the given dictionary"
                    " is not compliant with the given class type. Possible solutions:"
                    " 1) Create a new interface by modifying `class_type` input "
                    "argument, 2) reset all the interfaces with `reset` or 3) make the"
                    " dictionary compliant."
                )
        return dct

    @classmethod
    def reset(cls) -> None:
        self = cls()
        self.reset_custom_class_pyi()
        self.reset_loader_pyi()

    @final
    def generate_this_file_pyi(self) -> FileHandler:
        content = Path(__file__).read_text()

        # Prepend @overload decorator to load function
        file_handler = FileHandler(content)
        file_handler.remove_all_method_bodies()
        return file_handler

    def create_custom_class_pyi(self, string: str, class_name: str) -> None:
        custom_class_dir = Path(__file__).parent / self.custom_class_dir
        if not custom_class_dir.exists():
            os.makedirs(custom_class_dir)

        path = custom_class_dir / f"{class_name}.py"
        path.write_text(string)

    @final
    def add_new_class_to_loader_pyi(self, *, new_class: str, method_name: str) -> None:
        self._add_class_created_to_this_file_pyi(new_class)
        self._add_import_to_this_file_pyi(new_class)
        self._add_overload_to_this_file_pyi(new_class=new_class, method_name=method_name)

    @final
    def reset_loader_pyi(self) -> None:
        self.this_file_pyi = self.generate_this_file_pyi()
        self.update_this_file_pyi()

    @final
    def reset_custom_class_pyi(self) -> None:
        path = Path(__file__).parent / self.custom_class_dir
        if path.exists():
            shutil.rmtree(path)

    @final
    def _add_import_to_this_file_pyi(self, new_class: str) -> None:
        self.this_file_pyi.add_imports(
            f"from .build.{new_class} import {new_class}",
            in_type_checking_block=True,
        )
        self.update_this_file_pyi()

    @final
    def _add_overload_to_this_file_pyi(self, *, new_class: str, method_name: str) -> None:
        # First time the function is called it will attach an extra @overload decorator
        if not self.this_file_pyi.search_decorator("overload"):
            idx = self.this_file_pyi.search_method(
                method_name, return_index_above_decorator=True
            )
            if not idx:
                raise PyiGeneratorError(f"No method `{method_name}` could be found")

            self.this_file_pyi.add_line(idx[-1], f"{self.tab}@overload")

        string = (
            f"{self.tab}@overload\n{self.tab}@classmethod\n{self.tab}def {method_name}"
            f'(self, dct: MappingT, class_type: Literal["{new_class}"]) -> '
            f"{new_class}:\n{self.tab*2}...\n"
        )

        lines_found = self.this_file_pyi.search_method(
            method_name, return_index_above_decorator=True
        )
        self.this_file_pyi.add_line(lines_found[-1], string)
        self.update_this_file_pyi()

    @final
    def _add_class_created_to_this_file_pyi(self, new_class: str) -> None:
        label = "classes_created"

        value = self.this_file_pyi.search_assignment(label, only_values=True)[0]
        if not value:
            raise PyiGeneratorError(f"No `{label}` was found in this file.")
        # Case: Any
        if value == "Any":
            value = f'Union[Literal["{new_class}"], Any]'
        # Case: Union[Literal["A"], Any]
        else:
            value = value.replace("], Any]", f', "{new_class}"], Any]')

        self.this_file_pyi.replace_assignement(label, value)
        self.update_this_file_pyi()

    @final
    def update_this_file_pyi(self) -> None:
        self.this_file_pyi_path.write_text(str(self.this_file_pyi))
