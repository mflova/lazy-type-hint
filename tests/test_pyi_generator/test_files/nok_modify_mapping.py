from dynamic_pyi_generator.pyi_generator import PyiGenerator
from dynamic_pyi_generator.strategies import ParsingStrategies

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_dict": {"key1": "value1", "key2": "value2"},
    "nested_dict": {"key1": "value1", "key2": "value2"},
}

data = PyiGenerator(strategies=ParsingStrategies(dict_strategy="Mapping")).from_data(
    dct, class_name="Example"
)
data["list"] = [1, 2, 3]
