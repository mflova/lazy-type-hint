from lazy_type_hint import LazyTypeHintLive
from lazy_type_hint.strategies import ParsingStrategies

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_lst": [1, 2, 3],
}

data = LazyTypeHintLive(strategies=ParsingStrategies(list_strategy="Sequence")).from_data(
    dct, class_name="Example"
)
data["nested_lst"].append([1, 2])
