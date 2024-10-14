from typing import Any, Callable

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from lazy_type_hint.data_type_tree import data_type_tree_factory
from lazy_type_hint.strategies import ParsingStrategies


class TestLongSetOrSequence:
    @pytest.mark.parametrize("type_", [set, frozenset, list, tuple])
    def test_instantiation(self, type_: Any, benchmark: BenchmarkFixture) -> None:
        iterable = type_(list(range(1_000_000)))
        benchmark(
            lambda: data_type_tree_factory(
                iterable, name="Example", strategies=ParsingStrategies(check_max_n_elements_within_container=200)
            )
        )
        assert benchmark.stats.stats.mean < 0.008

    @pytest.mark.parametrize("type_", [set, frozenset, list, tuple])
    def test_get_str(self, type_: Any, benchmark: BenchmarkFixture) -> None:
        iterable = type_(list(range(1_000_000)))
        tree = data_type_tree_factory(
            iterable, name="Example", strategies=ParsingStrategies(check_max_n_elements_within_container=100)
        )

        benchmark(lambda: tree.get_str_all_nodes())
        assert benchmark.stats.stats.mean < 0.002


class TestDeepList:
    def test(self, benchmark: BenchmarkFixture, generate_tree_based_list: Callable[[int, int], list[Any]]) -> None:
        lst = generate_tree_based_list(depth=8, n_elements=3)  # type: ignore
        benchmark(
            lambda: data_type_tree_factory(
                lst, name="Example", strategies=ParsingStrategies(check_max_n_elements_within_container=250)
            ),
        )
        assert benchmark.stats.stats.mean < 1
