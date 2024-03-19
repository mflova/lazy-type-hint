from dynamic_pyi_generator.pyi_generator import PyiGenerator
from contextlib import suppress

dct = {
    "list": [1, 2, 3],
    "int": 10,
    "frozen_set": frozenset({1, 2, 3}),
}

data = PyiGenerator().from_data(dct, class_name="Example")
with suppress(AttributeError):
    data["frozen_set"].add([1, 2])
