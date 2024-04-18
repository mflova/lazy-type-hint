from lazy_type_hint import LazyTypeHintLive
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

lst = LazyTypeHintLive().from_data(lst, class_name="Example")
with suppress(KeyError):
    lst[0]["number"]
