from dataclasses import dataclass
from typing import Mapping

import pytest

from dynamic_pyi_generator.parser.parse_mapping import ParserMapping
from dynamic_pyi_generator.utils import TAB


class TestBuildTypedDict:
    @dataclass(frozen=True)
    class ParamsTest:
        """
        A test case for testing the parameters of a function.

        Attributes:
            name (str): The name of the test case.
            content (Mapping[str, str]): The content of the test case.
            functional_syntax (bool): Indicates whether the test case uses functional
                syntax.
            expected_output (str): The expected output of the test case.
        """

        name: str
        content: Mapping[str, str]
        functional_syntax: bool
        expected_output: str

    @pytest.mark.parametrize(
        "params_test",
        [
            ParamsTest(
                name="MyDict",
                content={"name": "str", "age": "int"},
                functional_syntax=False,
                expected_output=f"""class MyDict(TypedDict):
{TAB}name: str
{TAB}age: int""",
            ),
            ParamsTest(
                name="MyDict",
                content={"name": "str", "age": "int"},
                functional_syntax=True,
                expected_output=f"""MyDict = TypedDict(
{TAB}"MyDict",
{TAB}{{
{TAB}{TAB}"name": str,
{TAB}{TAB}"age": int,
{TAB}}},
)""",
            ),
            ParamsTest(
                name="MyDict",
                content={"name": "str", "age of the person": "AgeNumber"},
                functional_syntax=True,
                expected_output=f"""MyDict = TypedDict(
{TAB}"MyDict",
{TAB}{{
{TAB}{TAB}"name": str,
{TAB}{TAB}"age of the person": AgeNumber,
{TAB}}},
)""",
            ),
        ],
    )
    def test_build_typed_dict(self, params_test: ParamsTest) -> None:
        string = ParserMapping._build_typed_dict(  # noqa: SLF001
            name=params_test.name,
            content=params_test.content,
            functional_syntax=params_test.functional_syntax,
        )
        assert params_test.expected_output == string
