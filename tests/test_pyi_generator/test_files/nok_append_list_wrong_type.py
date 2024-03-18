from dynamic_pyi_generator.pyi_generator import PyiGenerator

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_lst": [1, 2, 3],
}

data = PyiGenerator().from_data(dct, class_name="Example")
data["nested_lst"].append(["2"])
