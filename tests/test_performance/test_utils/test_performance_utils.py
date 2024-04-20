from pytest_benchmark.fixture import BenchmarkFixture

from lazy_type_hint.utils.utils import (
    is_string_python_keyword_compatible,
)


class TestString:
    def test(self, benchmark: BenchmarkFixture) -> None:
        benchmark(lambda: is_string_python_keyword_compatible("MyClass"))
