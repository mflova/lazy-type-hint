import pytest

from dynamic_pyi_generator.testing_tools import Mypy


@pytest.fixture
def mypy() -> Mypy:
    return Mypy()
