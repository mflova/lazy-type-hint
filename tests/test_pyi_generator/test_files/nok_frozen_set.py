from lazy_type_hint import LazyTypeHintLive
from contextlib import suppress

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "frozen_set": frozenset({1, 2, 3}),
}

data = LazyTypeHintLive().from_data(dct, class_name="Example")
with suppress(AttributeError):
    data["frozen_set"].add([1, 2])
