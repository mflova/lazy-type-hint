from lazy_type_hint import LazyTypeHintLive
from lazy_type_hint.strategies import ParsingStrategies

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_dict": {"key1": "value1", "key2": "value2"},
    "nested_dict": {"key1": "value1", "key2": "value2"},
}

dct = LazyTypeHintLive(strategies=ParsingStrategies(dict_strategy="Mapping")).from_data(
    dct, class_name="Example"
)
dct["list"] = [1, 2, 3]
