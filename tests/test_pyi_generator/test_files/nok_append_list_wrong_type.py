from lazy_type_hint.lazy_type_hint import LazyTypeHint

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_lst": [1, 2, 3],
}

LazyTypeHint().reset()
data = LazyTypeHint().from_data(dct, class_name="Example")
data["nested_lst"].append(["2"])
