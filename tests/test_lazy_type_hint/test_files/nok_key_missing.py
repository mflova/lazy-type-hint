from lazy_type_hint import LazyTypeHintLive
from contextlib import suppress

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_dict": {"key1": "value1", "key2": "value2"},
}

data = LazyTypeHintLive().from_data(dct, class_name="Example")
with suppress(KeyError):
    data["new_key"]  # Mypy should raise error here
