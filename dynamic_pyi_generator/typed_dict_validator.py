from typing import Any, Mapping, get_type_hints


def validate_dict(data: Mapping[str, Any], typed_dict: Mapping[str, Any]):
    """
    Validates if a given dict `data` matches the type hints specified in `typed_dict`.

    Args:
        data (Mapping[str, Any]): The dictionary to be validated.
        typed_dict (Mapping[str, Any]): The type hints dictionary.

    Returns:
        bool: True if the dictionary matches the type hints, False otherwise.
    """
    dict_hints = get_type_hints(typed_dict)
    if data.keys() != dict_hints.keys():
        return False
    for key in data:
        if key not in dict_hints:
            return False

    for key, value_type in dict_hints.items():
        if key not in data:
            return False
        elif get_type_hints(value_type):  # If value is potentially a TypedDict with hints
            if not validate_dict(data[key], value_type):
                return False
        else:
            if not isinstance(data[key], value_type):
                return False
    return True
