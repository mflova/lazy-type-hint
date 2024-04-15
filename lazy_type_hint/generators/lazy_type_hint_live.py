import os
import re
import shutil
from pathlib import Path
from types import ModuleType
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Literal,  # noqa: F401
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    final,
    overload,  # noqa: F401
)

from typing_extensions import TypeAlias, override

import lazy_type_hint
from lazy_type_hint.file_modifiers.py_file_modifier import PyFileModifier
from lazy_type_hint.file_modifiers.yaml_file_modifier import YAML_COMMENTS_POSITION
from lazy_type_hint.generators.lazy_type_hint_abc import LazyTypeHintABC
from lazy_type_hint.strategies import ParsingStrategies
from lazy_type_hint.utils import (
    TAB,
    is_string_python_keyword_compatible,
)

THIS_DIR = Path(__file__).parent


class LazyTypeHintLiveError(Exception):
    """Raised by `LazyTypeHintLive` class."""


ObjectT = TypeVar("ObjectT")
PathT = TypeVar("PathT", str, Path)


class LazyTypeHintLive(LazyTypeHintABC):
    # Utils
    this_file_pyi: PyFileModifier
    """.pyi representation of this same module."""
    this_file_pyi_path: Path
    """Path to the .pyi file associated to this same module."""
    custom_classes_dir: Tuple[Union[ModuleType, str], ...]
    """Hold the information where the class interfaces will be created.
    
    First one is `ModuleType`. Following ones are strings. At least one must be provided.
    """
    strategies: ParsingStrategies
    """Strategies to follow when parsing the objects."""

    # Constants that should not be modified
    header: Final = "# Class automatically generated. DO NOT MODIFY."
    """Header that will be prepended to all new classes created."""
    classes_created: "TypeAlias" = Any
    """Classes created by the class. Do not modify."""
    methods_to_be_overloaded: Final = ("from_data", "from_yaml_file")
    """Methods that will be modified in the PYI interface when new classes are added."""

    @final
    def __init__(
        self,
        *,
        strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
        generated_classes_custom_dir: Tuple[Union[ModuleType, str], ...] = (
            lazy_type_hint,
            "build",
        ),
    ) -> None:
        self.custom_classes_dir = generated_classes_custom_dir
        self.strategies = strategies

        self.this_file_pyi_path = Path(__file__).with_suffix(".pyi")
        if not self.this_file_pyi_path.exists():
            self.this_file_pyi = self._generate_this_file_pyi()
        else:
            self.this_file_pyi = PyFileModifier(self.this_file_pyi_path.read_text(encoding="utf-8"))

    def _get_classes_added(self) -> Mapping[str, Path]:
        to_find = "classes_created"
        values = self.this_file_pyi.search_assignment("classes_created", only_values=True)
        if not values:
            raise LazyTypeHintLiveError(f"No `{to_find}` was found in this file.")

        if values[0] == "Any":
            return {}
        matches = re.findall(r'"(.*?)"', values[0])

        dct: Dict[str, Path] = {}
        for match in matches:
            path = Path(self._custom_class_dir_path / f"{match}.py")
            if not path.exists():
                raise LazyTypeHintLiveError(
                    f"A class `{match}` was apparently created but cannot find its "
                    f"corresponding source code within {self._custom_class_dir_path}"
                )
            dct[match] = path
        return dct

    @override
    def from_yaml_file(
        self,
        loader: Callable[[PathT], ObjectT],
        path: PathT,
        *,
        class_name: str,
        comments_are: Optional[Union[YAML_COMMENTS_POSITION, Sequence[YAML_COMMENTS_POSITION]]] = "side",
        **kwargs: Any,
    ) -> ObjectT:
        return super().from_yaml_file(loader=loader, path=path, class_name=class_name, comments_are=comments_are)  # type: ignore

    @override
    def from_data(
        self,
        data: ObjectT,
        class_name: str,
        **kwargs: Any,
    ) -> ObjectT:
        if not is_string_python_keyword_compatible(class_name):
            raise LazyTypeHintLiveError(
                f"Given class_name is not compatible with Python class naming conventions: {class_name}"
            )
        if class_name in self._get_classes_added():
            return data
        string_representation = str(super().from_data(data=data, class_name=class_name))
        string_representation = self.header + "\n" + string_representation
        self._create_custom_class_py(string_representation, class_name)
        self._add_new_class_to_loader_pyi(new_class=class_name)
        return data

    def reset(self) -> None:
        self._reset_custom_class_pyi()
        self.this_file_pyi = self._generate_this_file_pyi()
        self._update_this_file_pyi()

    @final
    def _generate_this_file_pyi(self) -> PyFileModifier:
        content = Path(__file__).read_text()

        file_handler = PyFileModifier(content)
        file_handler.remove_all_method_bodies()
        file_handler.remove_all_private_methods()
        file_handler.remove_all_instance_variables(class_name=(type(self)).__name__)
        return file_handler

    @property
    def _custom_class_dir_path(self) -> Path:
        package_path: Path = Path(self.custom_classes_dir[0].__path__[0])  # type: ignore
        sub_paths: Sequence[Path] = self.custom_classes_dir[1:]  # type: ignore

        for string in sub_paths:
            package_path = package_path / string
        return package_path

    def _create_custom_class_py(self, string: str, class_name: str) -> None:
        if not self._custom_class_dir_path.exists():
            os.makedirs(self._custom_class_dir_path)

        path = self._custom_class_dir_path / f"{class_name}.py"
        path.write_text(string)

    @final
    def _add_new_class_to_loader_pyi(self, *, new_class: str) -> None:
        self._add_class_created_to_this_file_pyi(new_class)
        self._add_import_to_this_file_pyi(new_class)
        for method_name in self.methods_to_be_overloaded:
            self._add_overload_to_this_file_pyi(new_class=new_class, method_name=method_name)

    @final
    def _reset_custom_class_pyi(self) -> None:
        if self._custom_class_dir_path.exists():
            shutil.rmtree(self._custom_class_dir_path)

    @final
    def _add_import_to_this_file_pyi(self, new_class: str) -> None:
        import_statement = (
            f"from {self.custom_classes_dir[0].__name__}."  # type: ignore
            f"{'.'.join(self.custom_classes_dir[1:])}.{new_class} import {new_class}"  # type: ignore
        )
        self.this_file_pyi.add_imports(
            import_statement,
            in_type_checking_block=False,
        )
        self._update_this_file_pyi()

    @final
    def _add_overload_to_this_file_pyi(
        self, *, new_class: str, method_name: str, input_argument: str = "class_name"
    ) -> None:
        # First time the function is called it will attach an extra @overload decorator
        if not self.this_file_pyi.search_decorator(decorator_name="overload", method_name=method_name):
            idx_lst = self.this_file_pyi.search_method(method_name, return_index_above_decorator=True)
            if not idx_lst:
                raise LazyTypeHintLiveError(f"No method `{method_name}` could be found")

            self.this_file_pyi.add_line(idx_lst[-1], f"{TAB}@overload")

        signature, _ = self.this_file_pyi.get_signature(method_name)

        # At this point idx is the index of the line where the input argument was found
        first_idx = signature.find(input_argument)
        if first_idx == -1:
            raise LazyTypeHintLiveError(f"No {input_argument} could be found within the signature {signature}")
        first_idx += len(input_argument)
        last_idx = first_idx
        while signature[last_idx] not in (",", ")"):
            last_idx += 1
        # The type hint of the input argument to modify is between first_idx and last_idx
        signature = signature[: first_idx + 1] + f' Literal["{new_class}"]' + signature[last_idx:]

        # Modifying returned value
        last_idx = signature.rfind(":")
        first_idx = signature.rfind("->")
        signature = signature[: first_idx + len("->") + 1] + new_class + signature[last_idx:]

        idx = self.this_file_pyi.search_method(method_name=method_name, return_index_above_decorator=True)[-1]
        self.this_file_pyi.add_line(idx, signature)
        self._update_this_file_pyi()

    @final
    def _add_class_created_to_this_file_pyi(self, new_class: str) -> None:
        label = "classes_created"

        value = self.this_file_pyi.search_assignment(label, only_values=True)[0]
        if not value:
            raise LazyTypeHintLiveError(f"No `{label}` was found in this file.")
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
