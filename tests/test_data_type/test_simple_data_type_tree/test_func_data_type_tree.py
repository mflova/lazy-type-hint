from typing import Final, List, Sequence

import pytest

from lazy_type_hint.data_type_tree.simple_data_type_tree.function_data_type_tree import FunctionDataTypeTree
from lazy_type_hint.utils import TAB


class TestLambda:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "data, expected_str",
        [
            [lambda: None, f"{NAME} = Callable[[], Any]"],
            [lambda x: None, f"{NAME} = Callable[[Any], Any]"],
            [lambda x, y: None, f"{NAME} = Callable[[Any, Any], Any]"],
            [lambda x, y, z: None, f"{NAME} = Callable[[Any, Any, Any], Any]"],
        ],
    )
    def test_get_str_top_node_lambda(self, data: object, expected_str: str) -> None:
        tree = FunctionDataTypeTree(data, self.NAME)
        assert expected_str == tree.get_str_top_node()
        assert "Any" in tree.imports
        assert "Callable" in tree.imports

    @pytest.mark.parametrize(
        "func1, func2, expected_out",
        [
            [lambda: None, lambda: None, True],
            [lambda x: None, lambda z: None, True],
            [lambda x, y: None, lambda z: None, False],
        ],
    )
    def test_hash(self, func1: object, func2: object, expected_out: bool) -> None:
        tree1 = FunctionDataTypeTree(func1, self.NAME)
        tree2 = FunctionDataTypeTree(func2, self.NAME)
        assert expected_out == (tree1._get_hash() == tree2._get_hash())


# fmt: off
def func1(): ...  # type: ignore
def func2() -> bool: ...  # type: ignore
def func3() -> Sequence[bool]: ...  # type: ignore
def func4(a: int): ...  # type: ignore
def func5(a: Sequence[int]): ...  # type: ignore
def func6(*, a: int): ...  # type: ignore
def func7(a: int, b: int, /, c: int): ...  # type: ignore
def func8(a: int, b: int, /, c: int, *, d: int): ...  # type: ignore
def func9(a, b, /, c, *, d): ...  # type: ignore
def func10(a, b, /, c, *, d): return 2  # type: ignore
def func11(a, b, /, c, *, d) -> Sequence[List[int]]: ...  # type: ignore
def func12(a: "TestFunction"): ...  # type: ignore
# fmt: on


class TestFunction:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "data, expected_out",
        [
            [func1, False],
            [func10, True],
        ],
    )
    def test_has_return(self, data: object, expected_out: bool) -> None:
        tree = FunctionDataTypeTree(data, self.NAME)
        assert expected_out == tree._has_return()

    @pytest.mark.parametrize(
        "data, expected_str, expected_imports",
        [
            [
                func1,
                f"""class {NAME}(Protocol):
{TAB}def __call__() -> None: ...""",
                set(),
            ],
            [
                func2,
                f"""class {NAME}(Protocol):
{TAB}def __call__() -> bool: ...""",
                set(),
            ],
            [
                func3,
                f"""class {NAME}(Protocol):
{TAB}def __call__() -> Sequence[bool]: ...""",
                set(),
            ],
            [
                func4,
                f"""class {NAME}(Protocol):
{TAB}def __call__(a: int) -> None: ...""",
                set(),
            ],
            [
                func5,
                f"""class {NAME}(Protocol):
{TAB}def __call__(a: Sequence[int]) -> None: ...""",
                {"Sequence"},
            ],
            [
                func6,
                f"""class {NAME}(Protocol):
{TAB}def __call__(*, a: int) -> None: ...""",
                set(),
            ],
            [
                func7,
                f"""class {NAME}(Protocol):
{TAB}def __call__(a: int, b: int, /, c: int) -> None: ...""",
                set(),
            ],
            [
                func8,
                f"""class {NAME}(Protocol):
{TAB}def __call__(a: int, b: int, /, c: int, *, d: int) -> None: ...""",
                set(),
            ],
            [
                func9,
                f"""class {NAME}(Protocol):
{TAB}def __call__(a, b, /, c, *, d) -> None: ...""",
                set(),
            ],
            [
                func10,
                f"""class {NAME}(Protocol):
{TAB}def __call__(a, b, /, c, *, d) -> Any: ...""",
                set(),
            ],
            [
                func11,
                f"""class {NAME}(Protocol):
{TAB}def __call__(a, b, /, c, *, d) -> Sequence[List[int]]: ...""",
                {"Sequence", "list"},
            ],
            [
                func12,
                f"""class {NAME}(Protocol):
{TAB}def __call__(a: 'TestFunction') -> None: ...""",
                set(),
            ],
        ],
    )
    def test_get_str_top_node(self, data: object, expected_str: str, expected_imports: str) -> None:
        tree = FunctionDataTypeTree(data, self.NAME)
        assert expected_str == tree.get_str_top_node()
        assert "Protocol" in tree.imports
        for expected_import in expected_imports:
            assert expected_import in tree.imports
