import os
import re
import shutil
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Dict, Final, Literal, Mapping, Optional, Sequence, Tuple, TypeVar, Union, final, overload
import lazy_type_hint
from lazy_type_hint.data_type_tree import data_type_tree_factory
from lazy_type_hint.file_modifiers.py_file_modifier import PyFileModifier
from lazy_type_hint.file_modifiers.yaml_file_modifier import YAML_COMMENTS_POSITION, YamlFileModifier
from lazy_type_hint.strategies import ParsingStrategies
from lazy_type_hint.utils import TAB, compare_str_via_ast, is_string_python_keyword_compatible
if TYPE_CHECKING:
    from typing_extensions import TypeAlias
THIS_DIR = Path(__file__).parent

class LazyTypeHintError(Exception):
    """Raised by `LazyTypeHint` class."""
ObjectT = TypeVar('ObjectT')
PathT = TypeVar('PathT', str, Path)

class LazyTypeHint:
    classes_created: 'TypeAlias' = Any
    'Classes created by the class. Do not modify.'
    @final
    def __init__(self, *, strategies: ParsingStrategies=ParsingStrategies(), if_interface_exists: Literal['overwrite', 'validate']='validate', generated_classes_custom_dir: Tuple[Union[ModuleType, str], ...]=(lazy_type_hint, 'build')) -> None:...

    def from_yaml_file(self, loader: Callable[[PathT], ObjectT], path: PathT, *, class_name: str, comments_are: Optional[Union[YAML_COMMENTS_POSITION, Sequence[YAML_COMMENTS_POSITION]]]='side') -> ObjectT:...

    def from_data(self, data: ObjectT, class_name: str) -> ObjectT:...

    def reset(self) -> None:...
