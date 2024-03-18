from dynamic_pyi_generator.pyi_generator import PyiGenerator

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "frozen_set": frozenset({1, 2, 3}),
}

data = PyiGenerator().from_data(dct, class_name="Example")
data["frozen_set"].add([1, 2])
