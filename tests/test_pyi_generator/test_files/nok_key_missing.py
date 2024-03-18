from dynamic_pyi_generator.pyi_generator import PyiGenerator

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_dict": {"key1": "value1", "key2": "value2"},
}

data = PyiGenerator().from_data(dct, class_name="Example")
data["new_key"]  # Mypy should raise error here
