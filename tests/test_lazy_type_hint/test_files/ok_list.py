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

lst = LazyTypeHintLive().from_data(lst, class_name="Example")
lst[0]["list"]
lst[0]["int"]
lst[0]["nested_dict"]
lst[0]["nested_dict"]["key1"]
