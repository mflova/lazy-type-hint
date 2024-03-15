from collections.abc import Mapping
from typing import Any, Set, List, Tuple

def parse(dct: Mapping[str, Any], new_class: str) -> str:
    header = "from typing import TypedDict"
    return header + _parse(dct, new_class)

def _parse(dct: Mapping[str, Any], new_class: str) -> str:
    tab = "    "
    string = f"\n\nclass {new_class}(TypedDict):"
    to_process: List[Tuple[str, Mapping[str, Any]]] = []

    for key, value in dct.items():
        if not isinstance(value, dict):
            string += f"\n{tab}{key}: {type(value).__name__}"
        else:
            class_to_be_created = new_class + key.capitalize()
            string += f"\n{tab}{key}: {class_to_be_created}"
            to_process.append((class_to_be_created, dct[key]))

    for class_to_be_created, dct in to_process:
        string += _parse(dct, class_to_be_created)
    return string
