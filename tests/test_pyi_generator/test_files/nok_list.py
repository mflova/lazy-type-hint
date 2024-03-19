from dynamic_pyi_generator.pyi_generator import PyiGenerator
from contextlib import suppress

lst = [
    {
        "list": [1, 2, 3],
        "int": 10,
        "nested_dict": {"key1": "value1", "key2": "value2"},
    },
    {
        "list": [1, 2, 5],
        "int": 10,
        "nested_dict": {"key1": "value1", "key2": "value2"},
    },
]

data = PyiGenerator().from_data(lst, class_name="Example")
with suppress(KeyError):
    data[0]["number"]
