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
            (pd.DataFrame({"A": [1]}))
            # (pd.DataFrame({("A",): [1, 2, 3]}))),  # TODO Fix test
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
            (pd.DataFrame({1: [1,2,3]}), f"{NAME}: TypeAlias = pd.DataFrame", 0),
            (pd.DataFrame({"A": [1,2,3], 1: [1,2,3]}), f"{NAME}: TypeAlias = pd.DataFrame", 0),
            (pd.DataFrame({"values": [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal["values"]) -> Union[pd.DataFrame, pd.Series]:
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
    def __getitem__(self, key: Literal["A"]) -> Union[pd.DataFrame, pd.Series]:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal["C"]) -> Union[pd.DataFrame, pd.Series]:
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
    def __getitem__(self, key: Literal["A"]) -> {NAME}A:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal["C"]) -> {NAME}C:
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
    def __getitem__(self, key: Literal["A"]) -> {NAME}A:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal["C"]) -> Union[pd.DataFrame, pd.Series]:
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
            (pd.DataFrame({("A", "B"): [1,2,3], "C": [1,2,3]}), f"""{NAME}: TypeAlias = pd.DataFrame""", 0),
            (pd.DataFrame({("A", "B"): [1,2,3], ("C", 1): [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal["A"]) -> ExampleA:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal["C"]) -> Union[pd.DataFrame, pd.Series]:
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
        assert expected_output == tree.get_str_top_node()


class TestGetStrPyFullTypeHint:
    NAME: Final = "Example"
    """Name that will be used to create the class."""
    STRATEGY: Final = ParsingStrategies(pandas_strategies="Full type hint")

    # fmt: off
    @pytest.mark.parametrize(
        "data, expected_output, expected_n_children",
        [
            (pd.DataFrame(), f"{NAME}: TypeAlias = pd.DataFrame", 0),
            (pd.DataFrame({1: [1,2,3]}), f"{NAME}: TypeAlias = pd.DataFrame", 0),
            (pd.DataFrame({"A": [1,2,3], 1: [1,2,3]}), f"{NAME}: TypeAlias = pd.DataFrame", 0),
            (pd.DataFrame({"values": [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal["values"]) -> Union[pd.DataFrame, pd.Series]:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal["values"],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 1),
            (pd.DataFrame({"A": [1,2,3], "C": [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal["A"]) -> Union[pd.DataFrame, pd.Series]:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal["C"]) -> Union[pd.DataFrame, pd.Series]:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal["A", "C"],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], ("C", "D"): [1,2,3]}), f"""class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal["A"]) -> {NAME}A:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal["C"]) -> {NAME}C:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal["A", "C"],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], ("C",): [1,2,3]}), f"""class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal["A"]) -> {NAME}A:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal["C"]) -> Union[pd.DataFrame, pd.Series]:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal["A", "C"],
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)""", 2),
            (pd.DataFrame({("A", "B"): [1,2,3], "C": [1,2,3]}), f"""{NAME}: TypeAlias = pd.DataFrame""", 0),
            (pd.DataFrame({("A", "B"): [1,2,3], ("C", 1): [1,2,3]}), """class Example(pd.DataFrame):

    @overload  # type: ignore
    def __getitem__(self, key: Literal["A"]) -> ExampleA:
        ...

    @overload  # type: ignore
    def __getitem__(self, key: Literal["C"]) -> Union[pd.DataFrame, pd.Series]:
        ...

    def __getitem__(
        self,
        key: Union[
            Literal["A", "C"],
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
        assert expected_output == tree.get_str_top_node()


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
