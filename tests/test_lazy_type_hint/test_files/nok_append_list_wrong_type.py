from lazy_type_hint import LazyTypeHintLive

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_lst": [1, 2, 3],
}

LazyTypeHintLive().reset()
dct = LazyTypeHintLive().from_data(dct, class_name="Example")
dct["nested_lst"].append(["2"])
