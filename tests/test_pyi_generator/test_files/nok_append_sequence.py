from lazy_type_hint.lazy_type_hint import LazyTypeHint
from lazy_type_hint.strategies import ParsingStrategies

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "nested_lst": [1, 2, 3],
}

data = LazyTypeHint(strategies=ParsingStrategies(list_strategy="Sequence")).from_data(
    dct, class_name="Example"
)
data["nested_lst"].append([1, 2])
