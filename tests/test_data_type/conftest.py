from types import MappingProxyType
from typing import Any, Callable, List, Literal, Mapping, cast

import pytest

SAMPLE_TYPE = Literal["frozenset", "set", "list", "tuple", "dictionary", "mapping"]


def random_func(a: int, b: Mapping[str, str]) -> List[bool]:  # type: ignore  # noqa: ARG001
    ...


samples: Mapping[SAMPLE_TYPE, Any] = {
    "list": [
        42,
        (3.14, "pi", {"key": "value"}),
        (1, 2, 3, ("nested", "tuple", [4, 5, 6])),
        [
            {"nested_dict_1": ["a", "b", "c"], "nested_set_1": {7, 8, 9}},
            [
                ("nested", "tuple", {"inner_key": ["inner_value_1", "inner_value_2"]}),
                [
                    {
                        "deep_dict": {"key_1": "value_1", "key_2": "value_2"},
                        "range_": range(1, 2),
                        "my_slice": slice(1, 2),
                    },
                    {"deep_set": {10, 11, 12}},
                    (13, 14, ["a", "b", "c"]),
                ],
            ],
            ("another", "tuple", [15, 16, 17]),
            ("function", lambda x: None),  # noqa: ARG005
            ("function2", random_func),
        ],
    ],
    "set": {
        "apple",
        (
            1,
            2,
            3,
            ("nested", "tuple", ("a", "b", "c")),
            range(1, 2),
        ),
    },
    "dictionary": {
        "integer": 42,
        "float": 3.14,
        "string": "Hello, world!",
        "boolean": True,
        "list": [1, 2, 3],
        "tuple": (4, 5, 6),
        "set": {7, 8, 9},
        "dictionary": {"key": "value"},
        "function": lambda x: None,  # noqa: ARG005
        "function2": random_func,
        "none": None,
        "nested_levels": {
            "level_1": {
                "set": {10, 11, 12},
                "dictionary": {"nested_key": "nested_value"},
                "tuple": (13, 14, 15),
                "level_2": {
                    "set": {16, 17, 18},
                    "dictionary": {"nested_key_2": "nested_value_2"},
                    "tuple": (19, 20, 21),
                    "level_3": {
                        "range_": range(1, 2),
                        "my_slice": slice(1, 2),
                        "set": {22, 23, 24},
                        "dictionary": {"nested_key_3": "nested_value_3"},
                        "tuple": (25, 26, 27),
                    },
                },
            }
        },
    },
}


@pytest.fixture
def create_sample() -> Callable[[str], Any]:
    """
    Create a sample object based on the given object type.

    Args:
        object_type (str): The type of object to create.

    Returns:
        str: The created sample object.
    """

    def _create_sample(object_type: SAMPLE_TYPE) -> Any:
        if object_type in samples:
            return samples[object_type]

        if object_type == "frozenset":
            return frozenset(samples["set"])
        if object_type == "tuple":
            return tuple(samples["list"])
        if object_type == "mapping":
            return MappingProxyType(samples["dictionary"])
        else:
            raise ValueError(f"There is no sample for the following data type: {object_type}")

    return cast(Callable[[str], Any], _create_sample)
