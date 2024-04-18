import pytest


@pytest.mark.usefixtures("_serial")
def _setup() -> None:
    """Execute all performance tests in a serial manner."""
    yield