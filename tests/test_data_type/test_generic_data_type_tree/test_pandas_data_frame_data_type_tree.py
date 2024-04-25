from typing import Final

import pandas as pd
import pytest

from lazy_type_hint.data_type_tree import data_type_tree_factory
from lazy_type_hint.data_type_tree.generic_type import PandasDataFrameDataTypeTree
from lazy_type_hint.strategies import ParsingStrategies


class TestInstantiation:
    @pytest.mark.parametrize(
        "data",
        [
            (pd.DataFrame()),
            (pd.DataFrame({"A": [1, 2, 3]})),
            (pd.DataFrame({"A": [1]})),
            (pd.DataFrame({("A",): [1, 2, 3]})),
        ],
    )
    def test(self, data: pd.DataFrame) -> None:
        data_type_tree_factory(data, name="Example")


class TestGetStrPyForAutocomplete:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    STRATEGY: Final = ParsingStrategies(pandas_strategies="Type hint only for autocomplete")

    # fmt: off
    @pytest.mark.parametrize(
        "data, expected_output, expected_n_children",
        [
            (pd.DataFrame(), f"{NAME}: TypeAlias = pd.DataFrame", 0),
            (pd.DataFrame({frozenset({1,2}): [1,2,3]}), f"{NAME}: TypeAlias = pd.DataFrame", 0),
            (pd.DataFrame({1: [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal[1]) -> pd.Series[int]:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 1),
            (pd.DataFrame({"values": [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['values']) -> pd.Series[int]:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 1),
            (pd.DataFrame({"A": [1,2,3], "C": [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> pd.Series[int]:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> pd.Series[int]:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], ("C", "D"): [1,2,3]}), f"""class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> {NAME}A:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> {NAME}C:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], ("C",): [1,2,3]}), f"""class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> {NAME}A:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> pd.DataFrame:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", frozenset({1})): [1,2,3], ("C",): [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> pd.DataFrame:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> pd.DataFrame:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({(2, "A"): [1,2,3], ("C",): [1,2,3]}), f"""class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal[2]) -> {NAME}2:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> pd.DataFrame:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({(True, "A"): [1,2,3], ("C",): [1,2,3]}), f"""class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal[True]) -> {NAME}True:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> pd.DataFrame:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], "C": [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> pd.Series[int]:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], ("C", 1): [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> ExampleA:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> ExampleC:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({"A": [1], 2: [2]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> pd.Series[int]:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal[2]) -> pd.Series[int]:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A",): [1], 2: [2]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal[2]) -> pd.Series[int]:
        ...

    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        ...

    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            str,
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
        ],
    )
    # fmt: on
    def test_get_str_top_node(
        self,
        data: pd.DataFrame,
        expected_output: str,
        expected_n_children: int,
    ) -> None:
        """
        Test the `get_str_top_node` method of the Tree class.

        Args:
            data (Mapping[Any, Any]): The input data for the test.
            expected_output (str): The expected output string.
            expected_n_children (int): The expected number of child nodes in the tree.
            strategies (Strategies): The strategies object.
            assert_imports (Callable[[DictDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        tree = PandasDataFrameDataTypeTree(data, name=self.NAME, strategies=self.STRATEGY)
        assert expected_n_children == len(tree)
        assert expected_output == tree.get_str_top_node(), f"Failed to type hint: \n{data}"


class TestGetStrPyFullTypeHint:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    STRATEGY: Final = ParsingStrategies(pandas_strategies="Full type hint")

    # fmt: off
    @pytest.mark.parametrize(
        "data, expected_output, expected_n_children",
        [
            (pd.DataFrame(), f"{NAME}: TypeAlias = pd.DataFrame", 0),
            (pd.DataFrame({1: [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal[1]) -> pd.Series[int]:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal[1],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 1),
            (pd.DataFrame({frozenset({1,2}): [1,2,3]}), f"{NAME}: TypeAlias = pd.DataFrame", 0),
            (pd.DataFrame({frozenset({1,2}): [1], "A": [1]}), f"{NAME}: TypeAlias = pd.DataFrame", 0),
            (pd.DataFrame({"values": [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['values']) -> pd.Series[int]:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal['values'],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 1),
            (pd.DataFrame({"A": [1,2,3], "C": [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> pd.Series[int]:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> pd.Series[int]:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal['A', 'C'],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], ("C", "D"): [1,2,3]}), f"""class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> {NAME}A:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> {NAME}C:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal['A', 'C'],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({(2, "B"): [1,2,3], ("C", "D"): [1,2,3]}), f"""class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal[2]) -> {NAME}2:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> {NAME}C:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal[2, 'C'],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({(True, "B"): [1,2,3], ("C", "D"): [1,2,3]}), f"""class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal[True]) -> {NAME}True:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> {NAME}C:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal[True, 'C'],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], ("C",): [1,2,3]}), f"""class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> {NAME}A:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> pd.DataFrame:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal['A', 'C'],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", frozenset({1,2})): [1,2,3], ("C",): [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> pd.DataFrame:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> pd.DataFrame:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal['A', 'C'],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], "C": [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> pd.Series[int]:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal['C'], Hashable,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], ("C", 1): [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> ExampleA:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal['C']) -> ExampleC:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal['A', 'C'],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({"A": [1,2,3], 1: [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal['A']) -> pd.Series[int]:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal[1]) -> pd.Series[int]:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal['A', 1],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A",): [1,2,3], 1: [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal[1]) -> pd.Series[int]:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal[1], Hashable,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
        ],
    )
    # fmt: on
    def test_get_str_top_node(
        self,
        data: pd.DataFrame,
        expected_output: str,
        expected_n_children: int,
    ) -> None:
        """
        Test the `get_str_top_node` method of the Tree class.

        Args:
            data (Mapping[Any, Any]): The input data for the test.
            expected_output (str): The expected output string.
            expected_n_children (int): The expected number of child nodes in the tree.
            strategies (Strategies): The strategies object.
            assert_imports (Callable[[DictDataTypeTree, Iterable[str]], None]): A callable that asserts the imports.
        """
        tree = PandasDataFrameDataTypeTree(data, name=self.NAME, strategies=self.STRATEGY)
        assert expected_n_children == len(tree)
        assert expected_output == tree.get_str_top_node(), f"Failed to type hint: \n{data}"


class TestGetStrsAllNodesUnformatted:
    @pytest.mark.parametrize(
        "strategy",
        [
            # ParsingStrategies(pandas_strategies="Do not type hint columns"),
            # ParsingStrategies(pandas_strategies="Full type hint"),
            ParsingStrategies(pandas_strategies="Type hint only for autocomplete"),
        ],
    )
    @pytest.mark.parametrize(
        "df",
        [
            pd.DataFrame({"a": [1]}),
            pd.DataFrame({1: [1]}),
            pd.DataFrame({frozenset({1, 2}): [1]}),
            pd.DataFrame({(1,): [1]}),
            pd.DataFrame({("1",): [1]}),
            pd.DataFrame({("1", "b"): [1]}),
            pd.DataFrame({("1", 2): [1]}),
        ],
    )
    def test(self, df: pd.DataFrame, strategy: ParsingStrategies) -> None:
        tree = data_type_tree_factory(df, name="Example", strategies=strategy)
        assert tree.get_strs_all_nodes_unformatted()


class TestHash:
    NAME: Final = "Example"
    """Name that will be used to create the class."""

    # fmt: off
    @pytest.mark.parametrize(
        "data1, data2, strategy, expected_equal",
        [
            (pd.DataFrame(), pd.DataFrame(), ParsingStrategies(pandas_strategies="Full type hint") ,True),
            (pd.DataFrame({"A": [1,2,3]}), pd.DataFrame(), ParsingStrategies(pandas_strategies="Full type hint") ,False),
            (pd.DataFrame({"A": [1,2,3]}), pd.DataFrame({"A": [1,2,3]}), ParsingStrategies(pandas_strategies="Full type hint") ,True),
            (pd.DataFrame({"A": [1,2,3]}), pd.DataFrame({"B": [1,2,3]}), ParsingStrategies(pandas_strategies="Full type hint") ,False),
            (pd.DataFrame({("A", "B"): [1,2,3]}), pd.DataFrame({"B": [1,2,3]}), ParsingStrategies(pandas_strategies="Full type hint") ,False),
            (pd.DataFrame(), pd.DataFrame(), ParsingStrategies(pandas_strategies="Do not type hint columns"), True),
            (pd.DataFrame({"A": [1,2,3]}), pd.DataFrame(), ParsingStrategies(pandas_strategies="Do not type hint columns"), True),
            (pd.DataFrame({"A": [1,2,3]}), pd.DataFrame({"A": [1,2,3]}), ParsingStrategies(pandas_strategies="Do not type hint columns"), True),
            (pd.DataFrame({"A": [1,2,3]}), pd.DataFrame({"B": [1,2,3]}), ParsingStrategies(pandas_strategies="Do not type hint columns"), True),
            (pd.DataFrame({("A", "B"): [1,2,3]}), pd.DataFrame({"B": [1,2,3]}), ParsingStrategies(pandas_strategies="Do not type hint columns"), True),
        ],
    )
    # fmt: on
    def test_get_str_top_node(
        self,
        data1: pd.DataFrame,
        data2: pd.DataFrame,
        strategy: ParsingStrategies,
        expected_equal: bool,
    ) -> None:
        """Test hash method."""
        tree1 = PandasDataFrameDataTypeTree(data1, name=self.NAME, strategies=strategy)
        tree2 = PandasDataFrameDataTypeTree(data2, name=self.NAME, strategies=strategy)
        assert expected_equal == ((tree1._get_hash()) == tree2._get_hash())
        assert expected_equal == (hash(tree1) == hash(tree2))
