from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    FrozenSet,
    Hashable,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    final,
)

from dynamic_pyi_generator.strategies import Strategies
from dynamic_pyi_generator.utils import TAB, ImportManager, cache_returned_value, is_string_python_keyword_compatible

if TYPE_CHECKING:
    from typing_extensions import Self


class DataTypeTreeError(Exception):
    ...


DataTypeT = TypeVar("DataTypeT")
ChildStructure = Union[FrozenSet[DataTypeT], Sequence[DataTypeT], Mapping[Hashable, DataTypeT]]


class DataTypeTree(ABC):
    name: str
    depth: int
    height: int
    imports: ImportManager  # Unique one shared among the whole tree
    parent: Optional[DataTypeTree]
    childs: Optional[ChildStructure[DataTypeTree]]
    simplify_redundant_types: bool
    holding_type: Type[object]
    strategies: Strategies

    data_type_tree_types: ClassVar[Mapping[Type[object], Type[DataTypeTree]]] = {}

    wraps: ClassVar[Union[Type[object], Sequence[Type[object]]]] = object

    @final
    def __init__(
        self,
        data: object,
        name: str,
        *,
        simplify_redundant_types: bool = True,
        imports: Optional[ImportManager] = None,
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
        self.imports = ImportManager() if imports is None else imports
        self.childs = self._get_childs(data)
        self.parent = parent
        self.height = self._get_height()
        self._needs_type_alias = False
        self.__post_init__()

    def __post_init__(self) -> None:
        ...

    def _get_height(self) -> int:
        max_height = 0
        for child in self:
            max_height = max(child.height, max_height)
        return max_height + 1

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

    @abstractmethod
    def _get_hash(self) -> object:
        ...

    @final
    def __hash__(self) -> int:
        return hash(self._get_hash())

    @abstractmethod
    def _get_str_py(self) -> str:
        ...

    @property
    def permission_to_create_type_alias(self) -> bool:
        for child in self:
            if child._needs_type_alias:
                return True
        return bool(self.height > self.strategies.min_height_to_define_type_alias)

    @final
    def get_str_no_type_alias_py(self) -> str:
        return self.get_str_py().split("=")[-1].strip()

    @final
    def get_str_py(self) -> str:
        return self._get_str_py().replace("NoneType", "None")

    @final
    @cache_returned_value
    def get_strs_recursive_py(self, *, include_imports: bool = True) -> Tuple[str, ...]:
        if self.depth == 0 and not self.childs:
            return (self.get_str_py(),)  # It will return a type alias for simple data types
        if not self.childs:
            return ()

        class_representations: List[str] = []
        for child in self:
            if child.permission_to_create_type_alias:
                class_representations.extend(child.get_strs_recursive_py(include_imports=False))
        class_representations.append(self.get_str_py())

        # These are available only when `get_str_py` is called
        if include_imports:
            return (self.imports.format(), *class_representations)
        return tuple(class_representations)

    @final
    def formatted_string(self, strs_py: Sequence[str]) -> str:
        strs_py = list(strs_py)
        if not strs_py:
            return ""
        for idx, line in enumerate(strs_py):  # noqa: B007
            if "" in line:
                break
        strs_py[idx] = strs_py[idx] + "\n"  # Add extra separation between imports
        return "\n\n".join(strs_py)

    @final
    def __str__(self) -> str:
        return self.formatted_string(self.get_strs_recursive_py(include_imports=True))

    @final
    def __repr__(self) -> str:
        return self.__str__()

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
