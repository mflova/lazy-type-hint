from typing import TYPE_CHECKING, overload

from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
from lazy_type_hint.strategies import ParsingStrategies

if TYPE_CHECKING:
    from types import MappingProxyType
    from typing import (
        Any,
        Dict,
        FrozenSet,
        List,
        Mapping,
        Optional,
        Sequence,
        Set,
        Tuple,
        Union,
    )

    from lazy_type_hint.data_type_tree.generic_type.dict_data_type_tree import DictDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.list_data_type_tree import ListDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.mapping_data_type_tree import MappingDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.sequence_data_type_tree import SequenceDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.set_data_type_tree import SetDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.tuple_data_type_tree import TupleDataTypeTree
    from lazy_type_hint.data_type_tree.simple_data_type_tree.simple_data_type_tree import SimpleDataTypeTree
    from lazy_type_hint.utils import ImportManager


@overload
def data_type_tree_factory(
    data: "List[Any]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "ListDataTypeTree":
    ...


@overload
def data_type_tree_factory(
    data: "Union[Set[Any], FrozenSet[Any]]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "SetDataTypeTree":
    ...


@overload
def data_type_tree_factory(
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
def data_type_tree_factory(
    data: "Tuple[Any, ...]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "TupleDataTypeTree":
    ...


@overload
def data_type_tree_factory(
    data: "Dict[Any, Any]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "DictDataTypeTree":
    ...


@overload
def data_type_tree_factory(
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
def data_type_tree_factory(
    data: "Union[Mapping[Any, Any], MappingProxyType[Any, Any]]",
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> "MappingDataTypeTree":
    ...


@overload
def data_type_tree_factory(
    data: object,
    name: str,
    *,
    imports: "Optional[ImportManager]" = None,
    depth: int = 0,
    strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
    parent: "Optional[DataTypeTree]" = None,
) -> DataTypeTree:
    ...


def data_type_tree_factory(
    data: object,
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
