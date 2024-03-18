from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Union

import pytest

from dynamic_pyi_generator.parser import Parser
from dynamic_pyi_generator.strategies import Strategies
from dynamic_pyi_generator.testing_tools import Mypy


class TestClassGenerator:
    @dataclass
    class ParamsTest:
        """
        Represents a test case for the Params class.

        Attributes:
            dct (Mapping[str, Any]): The input dictionary.
            expected_result (str): The expected result.
        """

        parser: Parser[Any]
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
                parser=Parser(
                    Strategies(
                        list_strategy="Sequence",
                        sequence_elements_strategy="Any",
                    )
                ),
                expected_result="lists_as_sequences_with_any.py",
            ),
            ParamsTest(
                parser=Parser(
                    Strategies(
                        list_strategy="Sequence",
                        sequence_elements_strategy="object",
                    )
                ),
                expected_result="lists_as_sequences_with_object.py",
            ),
            ParamsTest(
                parser=Parser(
                    Strategies(
                        list_strategy="Sequence",
                        sequence_elements_strategy="object",
                    )
                ),
                expected_result="lists_as_sequences_with_union.py",
            ),
            ParamsTest(
                parser=Parser(
                    Strategies(
                        list_strategy="list",
                        sequence_elements_strategy="Any",
                    )
                ),
                expected_result="lists_as_lists_with_any.py",
            ),
            ParamsTest(
                parser=Parser(
                    Strategies(
                        list_strategy="list",
                        sequence_elements_strategy="object",
                    )
                ),
                expected_result="lists_as_lists_with_object.py",
            ),
            ParamsTest(
                parser=Parser(
                    Strategies(
                        list_strategy="list",
                        sequence_elements_strategy="object",
                    )
                ),
                expected_result="lists_as_lists_with_union.py",
            ),
        ],
    )
    def test_parse_sequence_strategies(
        self, params_test: ParamsTest, mypy: Mypy, tmp_path: str
    ) -> None:
        self.launch_test(params_test=params_test, mypy=mypy, tmp_path=tmp_path)

    @pytest.mark.parametrize(
        "params_test",
        [
            ParamsTest(
                parser=Parser(
                    Strategies(
                        tuple_size_strategy="...",
                        tuple_elements_strategy="Any",
                    )
                ),
                expected_result="tuple_unsized_with_any.py",
            ),
            ParamsTest(
                parser=Parser(
                    Strategies(
                        tuple_size_strategy="...",
                        tuple_elements_strategy="object",
                    )
                ),
                expected_result="tuple_unsized_with_object.py",
            ),
            ParamsTest(
                parser=Parser(
                    Strategies(
                        tuple_size_strategy="...",
                        tuple_elements_strategy="Union",
                    )
                ),
                expected_result="tuple_unsized_with_union.py",
            ),
            ParamsTest(
                parser=Parser(
                    Strategies(
                        tuple_size_strategy="fixed",
                        tuple_elements_strategy="Any",
                    )
                ),
                expected_result="tuple_sized_with_any.py",
            ),
            ParamsTest(
                parser=Parser(
                    Strategies(
                        tuple_size_strategy="fixed",
                        tuple_elements_strategy="object",
                    )
                ),
                expected_result="tuple_sized_with_object.py",
            ),
            ParamsTest(
                parser=Parser(
                    Strategies(
                        tuple_size_strategy="fixed",
                        tuple_elements_strategy="Union",
                    )
                ),
                expected_result="tuple_sized_with_union.py",
            ),
        ],
    )
    def test_parse_tuple_strategies(
        self, params_test: ParamsTest, mypy: Mypy, tmp_path: str
    ) -> None:
        self.launch_test(params_test=params_test, mypy=mypy, tmp_path=tmp_path)

    @pytest.mark.parametrize(
        "params_test",
        [
            ParamsTest(
                parser=Parser(Strategies(set_elements_strategy="Any")),
                expected_result="set_with_any.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(set_elements_strategy="object")),
                expected_result="set_with_object.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(set_elements_strategy="Union")),
                expected_result="set_with_union.py",
            ),
        ],
    )
    def test_parse_set_strategies(
        self, params_test: ParamsTest, mypy: Mypy, tmp_path: str
    ) -> None:
        self.launch_test(params_test=params_test, mypy=mypy, tmp_path=tmp_path)

    @pytest.mark.parametrize(
        "params_test",
        [
            ParamsTest(
                parser=Parser(Strategies(mapping_strategy="TypedDict")),
                expected_result="dict_as_typed_dict.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(mapping_strategy="Dict")),
                expected_result="dict_as_dict.py",
            ),
            ParamsTest(
                parser=Parser(Strategies(mapping_strategy="Mapping")),
                expected_result="dict_as_mapping.py",
            ),
        ],
    )
    def test_parse_mapping_strategies(
        self, params_test: ParamsTest, mypy: Mypy, tmp_path: str
    ) -> None:
        self.launch_test(params_test=params_test, mypy=mypy, tmp_path=tmp_path)

    def launch_test(self, params_test: ParamsTest, mypy: Mypy, tmp_path: str) -> None:
        generated_str = params_test.parser.parse(params_test.dct, class_name="NewClass")
        new_file = Path(tmp_path) / "temp_file.py"
        new_file.write_text(generated_str)

        # self._update_files(generated_str, params_test=params_test)

        mypy_output = mypy.run(file=new_file, strict=True)
        error = (
            f"The generated string is not MYPY compliant: {mypy_output.errors_as_str()}"
        )
        assert mypy_output.success, error
        error = (
            "The generated string representation is not same as the expected one (see "
            f"{params_test.expected_result})"
        )
        assert generated_str == params_test.get_expected_str(), error

    def _update_files(self, string: str, params_test: ParamsTest) -> None:
        """Method used for developers."""
        Path(params_test.data_test_dir / params_test.expected_result).write_text(string)
