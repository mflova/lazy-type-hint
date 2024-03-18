from dynamic_pyi_generator.pyi_generator import PyiGenerator

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_lst": [1, 2, 3],
}

data = PyiGenerator(type_hint_strategy_for_list_elements="Any").from_data(
    dct, class_name="Example"
)
data["nested_lst"].append(["2"])

PyiGenerator().reset()
data = PyiGenerator(type_hint_strategy_for_list_elements="object").from_data(
    dct, class_name="Example"
)
data["nested_lst"].append(["2"])
