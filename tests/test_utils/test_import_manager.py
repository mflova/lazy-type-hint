from typing import Any

import pytest

from lazy_type_hint.utils import TAB
from lazy_type_hint.utils.import_manager import ImportManager


@pytest.fixture
def import_manager() -> ImportManager:
    return ImportManager()


@pytest.fixture(autouse=True)
def _assert_valid_code(import_manager: ImportManager) -> Any:
    yield
    try:
        exec(import_manager.format())
    except Exception as error:  # noqa: BLE001
        pytest.fail(f"Code generated is not valid: {error}")


class TestAdd:
    def test_import_manager_add(self, import_manager: ImportManager) -> None:
        import_manager.add("Protocol").add("Literal")
        assert import_manager._set == {"Protocol", "Literal"}


class TestFormatSinglePackage:
    def test_import_manager_format_single_package(self, import_manager: ImportManager) -> None:
        formatted_imports = import_manager._format_single_package("typing", ["Literal", "Protocol"], line_length=80)
        expected_output = "from typing import Literal, Protocol"
        assert expected_output == formatted_imports

    def test_import_manager_format_single_package_long_line(self, import_manager: ImportManager) -> None:
        formatted_imports = import_manager._format_single_package("typing", ["Literal", "Protocol"], line_length=30)
        expected_output = f"from typing import (\n{TAB}Literal,\n{TAB}Protocol,\n)"
        assert expected_output == formatted_imports

    def test_collections(self, import_manager: ImportManager) -> None:
        expected_output = "from collections.abc import Sequence"
        assert expected_output == import_manager.add("Sequence").format()


class TestAllUnknownSymbolsFromSignature:
    @pytest.mark.parametrize(
        "signature, expected_imports",
        [
            ("", set()),
            ("def (a: float):", set()),
            ("def (a: float, b: float):", set()),
            ("def (a: float, /, b: float):", set()),
            ("def (a: float, *, b: float):", set()),
            ("def (a: Sequence[int]):", {"Sequence"}),
            ("def (a: Sequence[int]) -> int:", {"Sequence"}),
            ("def (a: Sequence[int]) -> tuple[int, ...]:", {"Sequence"}),
        ],
    )
    def test_import_all_unknown_symbols_from_signature(
        self, import_manager: ImportManager, signature: str, expected_imports: set[str]
    ) -> None:
        import_manager.import_all_unkown_symbols_from_signature(signature=signature)
        assert expected_imports == import_manager._set

    def test_import_manager_format_no_imports(self, import_manager: ImportManager) -> None:
        formatted_imports = import_manager.format(line_length=80)
        expected_output = ""
        assert expected_output == formatted_imports


class TestFormat:
    def test_import_manager_format_short_line(self, import_manager: ImportManager) -> None:
        import_manager.add("Protocol").add("Literal").add("overload").add("MappingProxyType")
        formatted_imports = import_manager.format(line_length=120)
        expected_output = """from types import MappingProxyType
from typing import Literal, Protocol, overload"""
        assert expected_output == formatted_imports

    def test_import_manager_format_long_line(self, import_manager: ImportManager) -> None:
        import_manager.add("Protocol").add("Literal").add("overload").add("MappingProxyType")
        formatted_imports = import_manager.format(line_length=35)
        expected_output = """from types import MappingProxyType
from typing import (
    Literal,
    Protocol,
    overload,
)"""

        assert expected_output == formatted_imports

    def test_import_manager_format_no_imports(self, import_manager: ImportManager) -> None:
        formatted_imports = import_manager.format(line_length=80)
        expected_output = ""
        assert expected_output == formatted_imports
