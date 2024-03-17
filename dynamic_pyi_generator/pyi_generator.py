import importlib
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Final,
    Literal,
    Mapping,
    Set,
    TypeVar,
    Union,  # noqa: F401
    final,
    overload,  # noqa: F401
)

import dynamic_pyi_generator
from dynamic_pyi_generator.file_handler import FileHandler
from dynamic_pyi_generator.strategies import Strategies
from dynamic_pyi_generator.type_aliases import (
    LIST_ELEMENT_STRATEGIES,
    LIST_STRATEGIES,
    TUPLE_STRATEGIES,
)
from dynamic_pyi_generator.typed_dict_generator import Parser
from dynamic_pyi_generator.typed_dict_validator import validate_dict

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

THIS_DIR = Path(__file__).parent


class PyiGeneratorError(Exception): ...


MappingT = TypeVar("MappingT", bound=dict)


class PyiGenerator:
    # Utils
    parser: Parser
    """Generates string representation for the interface of the provided structure."""
    this_file_pyi: FileHandler
    """.pyi representation of this same module."""
    this_file_pyi_path: Path
    """Path to the .pyi file associated to this same module."""

    # Constants that should not be modified
    classes_created: "TypeAlias" = Any
    """Classes created by the class. Do not modify."""
    custom_class_dir_name: Final = "build"
    """Name of the direcotry that will contain all the generated stubs."""
    tab: Final = "    "
    """Tabs used whenever an indent is needed."""
    methods_to_be_overloaded: Final = ("from_dct", "from_file")
    """Methods that will be modified in the PYI interface when new classes are added."""

    @final
    def __init__(
        self,
        *,
        type_hint_lists_as_sequences: LIST_STRATEGIES = "list",
        type_hint_strategy_for_list_elements: LIST_ELEMENT_STRATEGIES = "Union",
        type_hint_strategy_for_tuple_elements: TUPLE_STRATEGIES = "fix size",
    ) -> None:
        self.this_file_pyi_path = Path(__file__).with_suffix(".pyi")
        if not self.this_file_pyi_path.exists():
            self.this_file_pyi = self._generate_this_file_pyi()
        else:
            self.this_file_pyi = FileHandler(
                self.this_file_pyi_path.read_text(encoding="utf-8")
            )
        self.parser = Parser(
            Strategies(
                list_strategy=type_hint_lists_as_sequences,
                list_elements_strategy=type_hint_strategy_for_list_elements,
                tuple_elements_strategy=type_hint_strategy_for_tuple_elements,
            )
        )

    def _get_classes_added(self) -> Mapping[str, Path]:
        to_find = "classes_created"
        values = self.this_file_pyi.search_assignment("classes_created", only_values=True)
        if not values:
            raise PyiGeneratorError(f"No `{to_find}` was found in this file.")

        if values[0] == "Any":
            return set()
        matches = re.findall(r'"(.*?)"', values[0])

        dct: Dict[str, str] = {}
        for match in matches:
            path = Path(self._custom_class_dir / f"{match}.py")
            if not path.exists():
                raise PyiGeneratorError(
                    f"A class `{match}` was apparently created but cannot find its corresponding source code within {self._custom_class_dir}"
                )
            dct[match] = path
        return dct

    @staticmethod
    def _find_line_idx(string: str, *, keyword: str) -> int:
        for idx, line in enumerate(string.split("\n")):
            if keyword in line:
                return idx
        raise PyiGeneratorError(
            f"It was not possible to find {keyword} among the lines of the given string."
        )

    def from_file(
        self,
        loader: Callable[[str], MappingT],
        path: str,
        class_type: str,
    ) -> MappingT:
        return self.from_dct(
            loader(path),
            class_type=class_type,
        )

    def from_dct(
        self,
        dct: MappingT,
        class_type: str,
    ) -> MappingT:
        typed_dict_representation = self.parser.parse(dct, new_class=class_type)
        classes_added = self._get_classes_added()
        if class_type not in classes_added:
            self._create_custom_class_pyi(typed_dict_representation, class_type)
            self._add_new_class_to_loader_pyi(new_class=class_type)
        else:
            if typed_dict_representation != classes_added[class_type].read_text():
                raise PyiGeneratorError(
                    f"An attempt to load a dictionary with an already existing class "
                    f"type ({class_type}) has been made. However, the given dictionary"
                    f" is not compliant with `{class_type}` type. Possible solutions:"
                    " 1) Create a new interface by modifying `class_type` input "
                    "argument, 2) reset all the interfaces with `reset` or 3) make the"
                    " input dictionary compliant."
                )
        return dct

    def reset(self) -> None:
        self._reset_custom_class_pyi()
        self.this_file_pyi = self._generate_this_file_pyi()
        self._update_this_file_pyi()

    @final
    def _generate_this_file_pyi(self) -> FileHandler:
        content = Path(__file__).read_text()

        # Prepend @overload decorator to load function
        file_handler = FileHandler(content)
        file_handler.remove_all_method_bodies()
        file_handler.remove_all_private_methods()
        file_handler.remove_all_instance_variables(class_name=(type(self)).__name__)
        return file_handler

    @property
    def _custom_class_dir(self) -> Path:
        return Path(__file__).parent / self.custom_class_dir_name

    def _create_custom_class_pyi(self, string: str, class_name: str) -> None:
        if not self._custom_class_dir.exists():
            os.makedirs(self._custom_class_dir)

        path = self._custom_class_dir / f"{class_name}.py"
        path.write_text(string)

    @final
    def _add_new_class_to_loader_pyi(self, *, new_class: str) -> None:
        self._add_class_created_to_this_file_pyi(new_class)
        self._add_import_to_this_file_pyi(new_class)
        for method_name in self.methods_to_be_overloaded:
            self._add_overload_to_this_file_pyi(
                new_class=new_class, method_name=method_name
            )

    @final
    def _reset_custom_class_pyi(self) -> None:
        path = Path(__file__).parent / self.custom_class_dir_name
        if path.exists():
            shutil.rmtree(path)

    @final
    def _add_import_to_this_file_pyi(self, new_class: str) -> None:
        self.this_file_pyi.add_imports(
            f"from .build.{new_class} import {new_class}",
            in_type_checking_block=True,
        )
        self._update_this_file_pyi()

    @final
    def _add_overload_to_this_file_pyi(
        self, *, new_class: str, method_name: str, input_argument: str = "class_type"
    ) -> None:
        # First time the function is called it will attach an extra @overload decorator
        if not self.this_file_pyi.search_decorator(
            decorator_name="overload", method_name=method_name
        ):
            idx = self.this_file_pyi.search_method(
                method_name, return_index_above_decorator=True
            )
            if not idx:
                raise PyiGeneratorError(f"No method `{method_name}` could be found")

            self.this_file_pyi.add_line(idx[-1], f"{self.tab}@overload")

        signature, _ = self.this_file_pyi.get_signature(method_name)

        # At this point idx is the index of the line where the input argument was found
        first_idx = signature.find(input_argument)
        first_idx += len(input_argument)
        last_idx = first_idx
        while signature[last_idx] not in (",", ")"):
            last_idx += 1
        # The type hint of the input argument to modify is between first_idx and last_idx
        signature = (
            signature[: first_idx + 1] + f' Literal["{new_class}"]' + signature[last_idx:]
        )

        # Modifying returned value
        last_idx = signature.rfind(":")
        first_idx = signature.rfind("->")
        signature = (
            signature[: first_idx + len("->") + 1] + new_class + signature[last_idx:]
        )

        idx = self.this_file_pyi.search_method(
            method_name=method_name, return_index_above_decorator=True
        )[-1]
        self.this_file_pyi.add_line(idx, signature)
        self._update_this_file_pyi()

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
        self._update_this_file_pyi()

    @final
    def _update_this_file_pyi(self) -> None:
        self.this_file_pyi_path.write_text(str(self.this_file_pyi))
