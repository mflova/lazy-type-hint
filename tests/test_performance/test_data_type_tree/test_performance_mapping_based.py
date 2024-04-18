from types import MappingProxyType
from typing import Any, Literal

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from lazy_type_hint.data_type_tree import data_type_tree_factory
from lazy_type_hint.strategies import ParsingStrategies


class TestLongMapping:
    """Expected quick tests, as these ones will only be checking for a few elements within the container."""

    @pytest.mark.parametrize("strategy", ["dict", "Mapping"])
    @pytest.mark.parametrize("type_", [dict, MappingProxyType])
    def test_instantiation(self, strategy: Literal["dict", "Mapping"], type_: Any, benchmark: BenchmarkFixture) -> None:
        n_elements = 1_000_000
        dct = type_(dict(zip(range(n_elements), range(n_elements))))
        benchmark(
            lambda: data_type_tree_factory(
                dct,
                name="Example",
                strategies=ParsingStrategies(dict_strategy=strategy, check_max_n_elements_within_container=100),
            ),
        )

        assert benchmark.stats.stats.mean < 4e-3

    @pytest.mark.parametrize("dict_strategy", ["dict", "Mapping"])
    @pytest.mark.parametrize("type_", [dict, MappingProxyType])
    def test_get_str(
        self, type_: Any, benchmark: BenchmarkFixture, dict_strategy: Literal["dict", "TypedDict"]
    ) -> None:
        n_elements = 1_000_000
        dct = type_(dict(zip(range(n_elements), range(n_elements))))
        tree = data_type_tree_factory(
            dct,
            name="Example",
            strategies=ParsingStrategies(check_max_n_elements_within_container=100, dict_strategy=dict_strategy),
        )

        benchmark(lambda: tree.get_str_all_nodes())
        assert benchmark.stats.stats.mean < 2e-5  # Quick as we are only check for a few elements


class TestLongTypedDict:
    """Expected long tests, as these ones will be checking for all elements within the container."""

    def test_instantiation(self, benchmark: BenchmarkFixture) -> None:
        n_elements = 5_000
        dct = dict(zip(range(n_elements), range(n_elements)))
        benchmark(
            lambda: data_type_tree_factory(
                dct,
                name="Example",
                strategies=ParsingStrategies(dict_strategy="TypedDict", check_max_n_elements_within_container=100),
            ),
        )

        assert benchmark.stats.stats.mean < 0.2

    def test_get_str(self, benchmark: BenchmarkFixture) -> None:
        n_elements = 5_000
        dct = dict(zip(range(n_elements), range(n_elements)))
        tree = data_type_tree_factory(
            dct,
            name="Example",
            strategies=ParsingStrategies(dict_strategy="TypedDict", check_max_n_elements_within_container=100),
        )

        benchmark(lambda: tree.get_str_all_nodes())
        assert benchmark.stats.stats.mean < 2e-5
