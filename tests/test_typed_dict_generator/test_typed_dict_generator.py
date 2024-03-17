from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import pytest

from dynamic_pyi_generator.strategies import Strategies
from dynamic_pyi_generator.testing_tools import Mypy
from dynamic_pyi_generator.typed_dict_generator import Parser


class TestTypedDictGenerator:
    @dataclass
    class ParamsTest:
        """
        Represents a test case for the Params class.

        Attributes:
            dct (Mapping[str, Any]): The input dictionary.
            expected_result (str): The expected result.
        """

        parser: Parser
        expected_result: str
        data_test_dir: Path = field(
            default=Path(__file__).parent / "test_files", init=False
        )
        dct: Mapping[str, Any] = field(
            default_factory=lambda: {
                "name": "John",
                "age": 25,
                "kids": ["Joan", "Peter"],
                "favourite_colors": {"red", "blue"},
                "random_data": [1, "Blue"],
                "tuple_example": (2, "Name"),
                "address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                },
            }
        )

        def get_expected_str(self) -> str:
            return (self.data_test_dir / self.expected_result).read_text()

    @pytest.mark.parametrize(
        "params_test",
        [
            ParamsTest(
                parser=Parser(Strategies(list_strategy="Sequence")),
                expected_result="lists_as_sequences.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(list_strategy="list")),
                expected_result="lists_as_lists.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(list_elements_strategy="Any")),
                expected_result="lists_any.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(list_elements_strategy="object")),
                expected_result="lists_object.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(list_elements_strategy="Union")),
                expected_result="lists_union.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(tuple_elements_strategy="Any")),
                expected_result="tuples_any.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(tuple_elements_strategy="fix size")),
                expected_result="tuples_fix_size.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(tuple_elements_strategy="object")),
                expected_result="tuples_object.py",
            ),
        ],
    )
    def test_parse(self, params_test: ParamsTest, mypy: Mypy, tmp_path: str) -> None:
        """
        Test the `parse` method of the `ParamsTest` class.

        Args:
            params_test (ParamsTest): An instance of the `ParamsTest` class.
            mypy (Mypy): An instance of the `Mypy` class.
            tmp_path (str): The temporary path for running the test.

        Raises:
            AssertionError: If the generated string representation is not MYPY compliant
                or not same as the expected one.
        """
        generated_str = params_test.parser.parse(params_test.dct, "NewClass")
        (Path(tmp_path) / "temp_file.py").write_text(generated_str)

        # self._update_files(generated_str, params_test=params_test)

        mypy_output = mypy.run(file=tmp_path, strict=True)
        error = (
            f"The generated string is not MYPY compliant: {mypy_output.errors_as_str()}"
        )
        assert mypy_output.success, error
        error = (
            "The generated string representation is not same as the expected one (see "
            f"{params_test.expected_result})"
        )
        assert generated_str == params_test.get_expected_str(), error

    def _update_files(self, string: str, params_test: ParamsTest):
        """Method used for developers."""
        Path(params_test.data_test_dir / params_test.expected_result).write_text(string)


class TestHelpers:
    DATA: Final = [
        {
            "name": "Manu",
            "age": 12,
        },
        {
            "name": "Manu",
            "age": 12,
            "new_key": "str",
        },
    ]

    def test_get_keys_not_in_common(self):
        assert Parser.get_keys_in_common(self.DATA) == {"name", "age"}

    def test_get_keys_in_common(self):
        assert Parser.get_keys_not_in_common(self.DATA) == {"new_key"}
