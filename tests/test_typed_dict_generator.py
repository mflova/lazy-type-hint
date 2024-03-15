from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pytest

from dynamic_pyi_generator.typed_dict_generator import parse


class TestTypedDictGenerator:
    @dataclass
    class ParamsTest:
        """
        Represents a test case for the Params class.

        Attributes:
            dct (Mapping[str, Any]): The input dictionary.
            expected_result (str): The expected result.
        """

        dct: Mapping[str, Any]
        expected_result: str

    @pytest.mark.parametrize(
        "params_test",
        [
            ParamsTest(
                dct={
                    "name": "John",
                    "age": 25,
                    "address": {
                        "street": "123 Main St",
                        "city": "New York",
                        "state": "NY",
                    },
                },
                expected_result="""from typing import TypedDict
class NewClass(TypedDict):
    name: str
    age: int
    address: NewClassAddress

class NewClassAddress(TypedDict):
    street: str
    city: str
    state: str""",
            )
        ],
    )
    def test_parse(self, params_test: ParamsTest) -> None:
        """
        Test the parse method of the ParamsTest class.

        Args:
            params_test (ParamsTest): An instance of the ParamsTest class containing
                the test parameters.
        """
        assert parse(params_test.dct, "NewClass") == params_test.expected_result
