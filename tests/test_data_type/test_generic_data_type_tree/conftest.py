from typing import Callable, Iterable

import pytest

from dynamic_pyi_generator.data_type_tree.data_type_tree import DataTypeTree


@pytest.fixture
def import_template() -> str:
    """
    Returns a string representing an import statement.

    The returned string is in the format "from {from} import {import}".

    Returns:
        str: The import statement template.
    """
    return "from {from_} import {import_}"


@pytest.fixture
def assert_imports() -> Callable[[DataTypeTree, Iterable[str]], None]:
    """
    Asserts that the given DataTypeTree contains all the necessary imports.

    Returns:
        Callable[[DataTypeTree, Iterable[str]], None]: A function that takes a DataTypeTree and a list of
            imports to check.

    Raises:
        AssertionError: If any of the expected imports are not found in the DataTypeTree.
    """
    generic_type_hints = ("Sequence", "List", "Tuple", "Dict", "Mapping", "Set", "FrozenSet", "TypedDict")

    def _assert_imports(tree: DataTypeTree, imports_to_check: Iterable[str]) -> None:
        for import_ in imports_to_check:
            import__ = (
                f" {import_}[" if import_ in generic_type_hints or f"{import_}(" in generic_type_hints else import_
            )
            if import__ in tree.get_str_top_node():
                assert (
                    import_ in tree.imports._set
                ), f"Not all needed imports were detected. Expected to import {import_} but only found {tree.imports._set}"

    return _assert_imports
