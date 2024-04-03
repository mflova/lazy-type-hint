from lazy_type_hint import LazyTypeHintLive

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

data = LazyTypeHintLive().from_data(lst, class_name="Example")
data[0]["list"]
data[0]["int"]
data[0]["nested_dict"]
data[0]["nested_dict"]["key1"]
