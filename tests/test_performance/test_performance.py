import timeit
from typing import Any, Callable, List

from lazy_type_hint.data_type_tree import data_type_tree_factory


class TestHash:
    def test(self, generate_tree_based_list: Callable[[int, int], List[Any]]) -> None:
        lst = generate_tree_based_list(depth=10, n_elements=3)  # type: ignore
        tree = data_type_tree_factory(lst, name="Example")

        time_before_cache = timeit.timeit(lambda: hash(tree), number=1)
        time_after_cache = timeit.timeit(lambda: hash(tree), number=1)

        assert time_after_cache < time_before_cache / 1_000
