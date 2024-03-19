from dynamic_pyi_generator.pyi_generator import PyiGenerator
from dynamic_pyi_generator.strategies import Strategies

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_lst": [1, 2, 3],
}

data = PyiGenerator(strategies=Strategies(sequence_elements_strategy="Any")).from_data(
    dct, class_name="Example"
)
data["nested_lst"].append(["2"])

PyiGenerator().reset()
data = PyiGenerator(strategies=Strategies(sequence_elements_strategy="object")).from_data(
    dct, class_name="Example"
)
data["nested_lst"].append(["2"])
