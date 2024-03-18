import os
import re
import shutil
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Dict, Final, Literal, Mapping, Sequence, Tuple, TypeVar, Union, final, overload
import dynamic_pyi_generator
from dynamic_pyi_generator.file_handler import FileHandler
from dynamic_pyi_generator.strategies import Strategies
from dynamic_pyi_generator.type_aliases import LIST_ELEMENT_STRATEGIES, LIST_STRATEGIES, TUPLE_STRATEGIES
from dynamic_pyi_generator.typed_dict_generator import Parser
if TYPE_CHECKING:
    from typing_extensions import TypeAlias
THIS_DIR = Path(__file__).parent

class PyiGeneratorError(Exception):
    """Raised by `PyiGenerator` class."""
DataT = TypeVar('DataT', Sequence[Any], Mapping[str, Any])

class PyiGenerator:
    classes_created: 'TypeAlias' = Any
    'Classes created by the class. Do not modify.'
    @final
    def __init__(self, *, type_hint_lists_as_sequences: LIST_STRATEGIES='list', type_hint_strategy_for_list_elements: LIST_ELEMENT_STRATEGIES='Union', type_hint_strategy_for_tuple_elements: TUPLE_STRATEGIES='fix size', generated_classes_custom_dir: Tuple[Union[ModuleType, str], ...]=(dynamic_pyi_generator, 'build')) -> None:...

    def from_file(self, loader: Callable[[str], DataT], path: str, class_type: str) -> DataT:...

    def from_data(self, data: DataT, class_type: str) -> DataT:...

    def reset(self) -> None:...
