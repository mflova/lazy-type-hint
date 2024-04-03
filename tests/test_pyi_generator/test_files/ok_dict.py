from lazy_type_hint.lazy_type_hint import LazyTypeHint

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_dict": {"key1": "value1", "key2": "value2"},
}

data = LazyTypeHint().from_data(dct, class_name="Example")
data["list"]
data["int"]
data["nested_dict"]["key1"]
