from typing import TYPE_CHECKING, Any, Union, overload
from collections.abc import Iterator

from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
from lazy_type_hint.strategies import ParsingStrategies

if TYPE_CHECKING:
    from types import MappingProxyType, ModuleType
    from typing import (
        Optional,
        TextIO,
    )
    from collections.abc import Iterator, Mapping, Sequence

    import numpy as np
    import pandas as pd
    from numpy.typing import NDArray

    from lazy_type_hint.data_type_tree.generic_type.dict_data_type_tree import DictDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.iterator_data_type_tree import IteratorDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.list_data_type_tree import ListDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.mapping_data_type_tree import MappingDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.mapping_proxy_data_type_tree import MappingProxyDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.pandas_data_frame_data_type_tree import PandasDataFrameDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.pandas_series_data_type_tree import (
        PandasSeriesDataTypeTree,
    )
    from lazy_type_hint.data_type_tree.generic_type.sequence_data_type_tree import SequenceDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.set_data_type_tree import SetDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.tuple_data_type_tree import TupleDataTypeTree
    from lazy_type_hint.data_type_tree.simple_data_type_tree.io_data_type_tree import IoDataTypeTree
    from lazy_type_hint.data_type_tree.simple_data_type_tree.module_data_type_tree import ModuleTypeDataTypeTree
    from lazy_type_hint.data_type_tree.simple_data_type_tree.numpy_data_type_tree import NumpyDataTypeTree
    from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import SimpleDataTypeTree
    from lazy_type_hint.utils import ImportManager


@overload
def data_type_tree_factory(  # type: ignore[overload-overlap]
    data: "NDArray[np.generic]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "NumpyDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[overload-overlap]
    data: "MappingProxyType[Any, Any]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "MappingProxyDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[overload-overlap]
    data: "Iterator[Any]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "IteratorDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[overload-overlap]
    data: "ModuleType",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "ModuleTypeDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[overload-overlap]
    data: "TextIO",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "IoDataTypeTree":
    ...


@overload
def data_type_tree_factory(
    data: "pd.Series[Any]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "PandasSeriesDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[misc]
    data: "pd.DataFrame",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "PandasDataFrameDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[misc]
    data: "list[Any]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "ListDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[misc]
    data: "Union[type[Any], frozenset[Any]]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "SetDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[misc]
    data: "Union[bool, float, slice, None]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "SimpleDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[misc]
    data: "tuple[Any, ...]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "TupleDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[misc]
    data: "dict[Any, Any]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "DictDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[misc]
    data: "Sequence[Any]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "SequenceDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[misc]
    data: "Mapping[Any, Any]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "MappingDataTypeTree":
    ...


@overload
def data_type_tree_factory(  # type: ignore[misc]
    data: Union[object, Any],
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> DataTypeTree:
    ...


def data_type_tree_factory(
    data: Union[object, Any],
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> DataTypeTree:
    return DataTypeTree.get_subclass(data)(
        data=data, name=name, imports=imports, depth=depth, strategies=strategies, parent=parent
    )
