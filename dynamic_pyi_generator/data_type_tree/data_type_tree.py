from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Final,
    FrozenSet,
    Hashable,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    final,
)

from dynamic_pyi_generator.strategies import Strategies
from dynamic_pyi_generator.utils import TAB, cache_returned_value, is_string_python_keyword_compatible

if TYPE_CHECKING:
    from typing_extensions import Self


class DataTypeTreeError(Exception):
    ...


DataTypeT = TypeVar("DataTypeT")
ChildStructure = Union[FrozenSet[DataTypeT], Sequence[DataTypeT], Mapping[Hashable, DataTypeT]]


class DataTypeTree(ABC):
    name: str
    depth: int
    imports: Set[str]  # Unique one shared among the whole tree
    parent: Optional[DataTypeTree]
    childs: Optional[ChildStructure[DataTypeTree]]
    simplify_redundant_types: bool
    holding_type: Type[object]
    strategies: Strategies

    data_type_tree_types: ClassVar[Mapping[Type[object], Type[DataTypeTree]]] = {}

    wraps: ClassVar[Union[Type[object], Sequence[Type[object]]]] = object
    suffix_used_for_same_class_name: Final = "_{idx}"

    @final
    def __init__(
        self,
        data: object,
        name: str,
        *,
        simplify_redundant_types: bool = True,
        imports: Optional[Set[str]] = None,
        depth: int = 0,
        strategies: Strategies = Strategies(),  # noqa: B008
        parent: Optional[DataTypeTree] = None,
    ) -> None:
        # Validation
        self._validate_name(name)
        wraps = self.wraps if isinstance(self.wraps, Iterable) else [self.wraps]
        if type(data) not in wraps:
            wraps_str = [element.__name__ for element in wraps]
            raise DataTypeTreeError(
                f"The given parser is meant to parse `{', '.join(wraps_str)}` data type but "
                f"{type(data).__name__} was given"
            )
        self.name = name
        self.holding_type = type(data)
        self.strategies = strategies
        self.simplify_redundant_types = simplify_redundant_types
        self.depth = depth
        self.imports = set() if imports is None else imports
        self.childs = self._get_childs(data)
        self.parent = parent

    @staticmethod
    def _validate_name(name: str) -> None:
        if not is_string_python_keyword_compatible(name):
            raise DataTypeTreeError(f"The given name ({name}) is not Python-keyword compatible")

    @abstractmethod
    def _get_childs(self, data: object) -> Optional[ChildStructure[DataTypeTree]]:
        ...

    @final
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        wraps = cls.wraps if isinstance(cls.wraps, Iterable) else [cls.wraps]
        for type_ in wraps:
            if type_ != object:
                if type_ in cls.data_type_tree_types:
                    raise DataTypeTreeError(f"A parser for {type_.__name__} was already found")
                cls.data_type_tree_types[type_] = cls  # type: ignore

    @final
    def __hash__(self) -> int:
        return id(self.get_strs_recursive_py(include_imports=False))

    @abstractmethod
    def _get_str_py(self) -> str:
        ...

    @final
    def get_str_py(self) -> str:
        return self._get_str_py().replace("NoneType", "None")

    @final
    @cache_returned_value
    def get_strs_recursive_py(self, *, include_imports: bool = True) -> Tuple[str, ...]:
        if not self.childs:
            return ()

        class_representations: List[str] = []
        for child in self:
            class_representations.extend(child.get_strs_recursive_py(include_imports=False))
        class_representations.append(self.get_str_py())

        # These are available only when `get_str_py` is called
        if include_imports:
            return tuple(sorted(self.imports) + class_representations)
        return tuple(class_representations)

    def __str__(self) -> str:
        return f"{type(self).__name__}"

    @abstractmethod
    def __iter__(self) -> Self:
        """Get an iterator to iterate over the childs of the tree."""

    @final
    def __len__(self) -> int:
        if self.childs is None:
            return 0
        return len(self.childs)

    @abstractmethod
    def __next__(self) -> DataTypeTree:
        """Iterate over the childs of the tree."""

    @final
    def print_childs(self) -> None:
        if self.depth == 0:
            print(type(self).__name__)
        for child in self:
            print(f"{TAB*child.depth} - {child}")
            child.print_childs()

    @final
    def __repr__(self) -> str:
        return self.__str__()

    @final
    def __eq__(self, other_object: object) -> bool:
        if type(self) is type(other_object):
            return hash(self) == hash(other_object)
        return False

    @classmethod
    def get_data_type_tree_for_type(cls, type_: Type[object]) -> Type[DataTypeTree]:
        try:
            return cls.data_type_tree_types[type_]
        except KeyError as error:
            raise DataTypeTreeError(
                f"There is no tree representation for the given data type: {type_.__name__}"
            ) from error
