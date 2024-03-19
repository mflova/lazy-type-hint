import os
import re
import shutil
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Dict, Final, Literal, Mapping, Sequence, Tuple, TypeVar, Union, final, overload
import dynamic_pyi_generator
from dynamic_pyi_generator.file_handler import FileHandler
from dynamic_pyi_generator.parser import Parser
from dynamic_pyi_generator.strategies import Strategies
from dynamic_pyi_generator.utils import TAB, compare_strings_via_ast, is_string_python_keyword_compatible
if TYPE_CHECKING:
    from typing_extensions import TypeAlias
THIS_DIR = Path(__file__).parent

class PyiGeneratorError(Exception):
    """Raised by `PyiGenerator` class."""
ObjectT = TypeVar('ObjectT')

class PyiGenerator:
    classes_created: 'TypeAlias' = Any
    'Classes created by the class. Do not modify.'
    @final
    def __init__(self, *, type_hint_lists_as_sequences: LIST_STRATEGIES='list', type_hint_strategy_for_list_elements: LIST_ELEMENT_STRATEGIES='Union', type_hint_strategy_for_tuple_size: TUPLE_SIZE_STRATEGIES='fixed', type_hint_strategy_for_tuple_elements: TUPLE_ELEMENT_STRATEGIES='Union', type_hint_strategy_for_set_elements: SET_STRATEGIES='Union', type_hint_strategy_for_mapping: MAPPING_STRATEGIES='TypedDict', generated_classes_custom_dir: Tuple[Union[ModuleType, str], ...]=(dynamic_pyi_generator, 'build')) -> None:...

    def from_file(self, loader: Callable[[str], ObjectT], path: str, class_name: str) -> ObjectT:...

    def from_data(self, data: ObjectT, class_name: str) -> ObjectT:...

    def reset(self) -> None:...
