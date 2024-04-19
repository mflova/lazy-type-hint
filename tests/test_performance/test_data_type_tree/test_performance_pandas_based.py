from types import MappingProxyType
from typing import Any, Literal

import pandas as pd
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from lazy_type_hint.data_type_tree import data_type_tree_factory
from lazy_type_hint.strategies import ParsingStrategies


def dataframe_factory(*, n_columns: int, column_depth: int) -> pd.DataFrame:
    if column_depth == 1:
        return pd.DataFrame({k: [1] for k in range(n_columns)})
    else:
        return pd.DataFrame({(1,) * column_depth: [1]})


class TestManyColumns:
    def test_instantiation(self, benchmark: BenchmarkFixture) -> None:
        df = dataframe_factory(n_columns=100_000, column_depth=1)
        benchmark(lambda: data_type_tree_factory(df, name="Example"))
        assert benchmark.stats.stats.mean < 0.05

    def test_get_str(self, benchmark: BenchmarkFixture) -> None:
        df = dataframe_factory(n_columns=100_000, column_depth=1)

        def launcher():
            tree = data_type_tree_factory(df, name="Example")
            benchmark(lambda: tree.get_str_all_nodes())

        launcher()
        assert benchmark.stats.stats.mean < 1e-5


class TestDeepColumns:
    def test_instantiation(self, benchmark: BenchmarkFixture) -> None:
        df = dataframe_factory(n_columns=1, column_depth=1_000)
        benchmark(lambda: data_type_tree_factory(df, name="Example"))
        assert benchmark.stats.stats.mean < 0

    def test_get_str(self, benchmark: BenchmarkFixture) -> None:
        df = dataframe_factory(n_columns=1, column_depth=1_000)

        def launcher():
            tree = data_type_tree_factory(df, name="Example")
            benchmark(lambda: tree.get_str_all_nodes())

        launcher()
        assert benchmark.stats.stats.mean < 0
