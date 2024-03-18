from dynamic_pyi_generator.pyi_generator import PyiGenerator

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
data[0]["list"]
data[0]["int"]
data[0]["nested_dict"]
data[0]["nested_dict"]["key1"]
