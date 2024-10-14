import contextlib
import os
import random
from pathlib import Path
from typing import Any, Callable
from collections.abc import Generator

import filelock
import pytest
from filelock import BaseFileLock

import lazy_type_hint.generators
from lazy_type_hint.generators.lazy_type_hint_live import LazyTypeHintLive
from lazy_type_hint.utils import Mypy


@pytest.fixture
def mypy() -> Mypy:
    return Mypy()


@pytest.fixture(scope="session")
def lock(tmp_path_factory: pytest.TempPathFactory) -> Any:
    base_temp = tmp_path_factory.getbasetemp()
    lock_file = base_temp.parent / "serial.lock"
    yield filelock.FileLock(lock_file=str(lock_file))
    with contextlib.suppress(OSError):
        os.remove(path=lock_file)


@pytest.fixture
def _serial(lock: BaseFileLock) -> Any:
    """Use this fixture to execute tests in a serial manner."""
    with lock.acquire(poll_interval=0.1):
        LazyTypeHintLive.reset()
        try:
            yield
        finally:
            LazyTypeHintLive.reset()


@pytest.fixture(scope="session", autouse=True)
def _teardown() -> Any:
    for path in Path(lazy_type_hint.generators.__path__[0]).glob("*.pyi"):
        os.remove(path)


@pytest.fixture(autouse=True)
def _test_no_print_statements(
    capsys: pytest.CaptureFixture[Any],
) -> Generator[None, None, None]:
    """Verify that no print statements were added in any of these tests."""
    yield
    captured = capsys.readouterr()
    msg = "Print statements were detected for the checks."
    assert not captured.out, msg
    assert not captured.err, msg


@pytest.fixture
def generate_tree_based_list() -> Callable[[int, int], list[Any]]:
    def _generate_tree_based_list(depth: int, n_elements: int) -> list[Any]:
        def append_elem(lst: list[Any], depth: int, n_elements: int, curr_depth: int = 0) -> None:
            if curr_depth >= depth:
                lst.append(random.choice([{1, 2, 3}, {"a": 1, "b": 2}, [1, 2, 3], (1, 2, 3)]))
                return

            for _ in range(n_elements):
                new_lst: list[Any] = []
                append_elem(new_lst, depth=depth, n_elements=n_elements, curr_depth=curr_depth + 1)
                lst.append(new_lst)

        lst: list[Any] = []
        append_elem(lst, depth=depth, n_elements=n_elements)
        return lst

    return _generate_tree_based_list
