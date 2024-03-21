import contextlib
import os
from typing import Any

import filelock
import pytest
from filelock import BaseFileLock

from dynamic_pyi_generator.pyi_generator import PyiGenerator
from dynamic_pyi_generator.testing_tools import Mypy


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
        PyiGenerator().reset()
        yield
        PyiGenerator().reset()
