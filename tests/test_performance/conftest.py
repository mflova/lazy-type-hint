from typing import Any

import pytest


@pytest.mark.usefixtures("_serial")
def _setup() -> Any:
    """Execute all performance tests in a serial manner."""
    yield
