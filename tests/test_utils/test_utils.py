from typing import Any

import pytest

from lazy_type_hint.utils import (
    cache_returned_value_per_instance,
    is_string_python_keyword_compatible,
)


@pytest.mark.parametrize(
    "string, expected_output",
    [
        ("build0", True),
        ("bu_ild", True),
        ("_build0", True),
        (".build", False),
        ("bu.ild", False),
        ("bu ild", False),
        ("0build", False),
    ],
)
def test_is_string_python_keyword_compatible(string: str, expected_output: bool) -> None:
    """
    Test function for checking if a string is compatible with Python keywords.

    Args:
        string (str): The string to be checked.
        expected_output (bool): The expected output of the function.

    Returns:
        None: This function does not return anything.

    Raises:
        AssertionError: If the expected output does not match the actual output.
    """
    assert expected_output == is_string_python_keyword_compatible(string)


class TestCacheReturnedValue:
    class DummyClass:
        """Class that will be used for testing purposes."""

        def __init__(self) -> None:
            self.cache_attr = None

        @cache_returned_value_per_instance
        def dummy_method(self, arg: Any) -> Any:
            self.cache_attr = arg
            return arg

    def test_cache_returned_value(self) -> None:
        dummy_obj = self.DummyClass()

        # Test initial call
        result = dummy_obj.dummy_method(10)
        assert result == 10
        assert dummy_obj.cache_attr == 10

        # Test cached call
        result = dummy_obj.dummy_method(20)
        assert result == 10
        assert dummy_obj.cache_attr == 10
