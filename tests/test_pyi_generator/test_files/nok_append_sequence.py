from dynamic_pyi_generator.pyi_generator import PyiGenerator
from dynamic_pyi_generator.strategies import Strategies

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_lst": [1, 2, 3],
}

data = PyiGenerator(strategies=Strategies(list_strategy="Sequence")).from_data(
    dct, class_name="Example"
)
data["nested_lst"].append([1, 2])
