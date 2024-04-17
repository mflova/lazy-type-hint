import random
from typing import Any, Callable, List

import pytest


@pytest.fixture
def generate_tree_based_list() -> Callable[[int, int], List[Any]]:
    def _generate_tree_based_list(depth: int, n_elements: int) -> List[Any]:
        def append_elem(lst: List[Any], depth: int, n_elements: int, curr_depth: int = 0) -> None:
            if curr_depth >= depth:
                lst.append(random.choice([{1, 2, 3}, {"a": 1, "b": 2}, [1, 2, 3], (1, 2, 3)]))
                return

            for _ in range(n_elements):
                new_lst: List[Any] = []
                append_elem(new_lst, depth=depth, n_elements=n_elements, curr_depth=curr_depth + 1)
                lst.append(new_lst)

        lst: List[Any] = []
        append_elem(lst, depth=depth, n_elements=n_elements)
        return lst

    return _generate_tree_based_list
