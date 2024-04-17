"""`DataTypeTree` object that creates a tree representing all container types within the data type given.

This data can then be parsed to a .py compatible file that will type hint your code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    FrozenSet,
    Hashable,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    final,
)

from lazy_type_hint.strategies import ParsingStrategies
from lazy_type_hint.utils import (
    ImportManager,
    OrderedSet,
    cache_returned_value,
    is_string_python_keyword_compatible,
)

if TYPE_CHECKING:
    from typing_extensions import Self


class DataTypeTreeError(Exception):
    ...


DataTypeT = TypeVar("DataTypeT", bound=object)
ChildrenStructure = Union[FrozenSet[DataTypeT], Sequence[DataTypeT], Mapping[Hashable, DataTypeT]]
"""Different child structures that the Tree can hold."""


class DataTypeTree(ABC):
    """Tree that represents any kind of data with its inner structures."""

    name: str
    """Name that represents this node."""
    depth: int
    """Depth of the current node with respect to the whole tree."""
    height: int
    """Maximum height among all the child nodes."""
    data: object
    """Data that was given as input to parse.
    
    This one might have been modified with respect to the original one.
    """
    imports: ImportManager  # Unique one shared among the whole tree
    """Handle the imports required to generate the string representation."""
    parent: Optional[DataTypeTree]
    """Parent node (if any)."""
    children: Optional[ChildrenStructure[DataTypeTree]]
    """All children available within the tree."""
    holding_type: Type[object]
    """Type of input data given."""
    strategies: ParsingStrategies
    """Strategies to follow when parsing the data."""

    subclasses: ClassVar[Mapping[Type[object], Type[DataTypeTree]]] = {}
    """Available subclasses according to the type they are able to parse."""
    wraps: ClassVar[Sequence[Type[object]]] = (object,)
    """Object type that the tree is able to parse."""

    _cached_hash: Optional[int]
    """Pre-computed hash of the instance assuming the inner state of the DataTypeTree does not change."""

    @final
    def __init__(
        self,
        data: object,
        name: str,
        *,
        imports: Optional[ImportManager] = None,
        depth: int = 0,
        strategies: ParsingStrategies = ParsingStrategies(),  # noqa: B008
        parent: Optional[DataTypeTree] = None,
    ) -> None:
        # Validation
        self._validate_name(name)
        self._check_tree_is_correct_one(data)

        self.data = data
        self.name = name
        self._cached_hash = None
        self.holding_type = type(data)
        self.strategies = strategies
        self.depth = depth
        self.imports = ImportManager() if imports is None else imports
        self.parent = parent
        self.__pre_child_instantiation__()
        self.children = self._instantiate_children(self.data)
        self.height = self._get_height()
        self.__post_child_instantiation__()

    @classmethod
    def get_subclass(cls, data: object) -> Type[DataTypeTree]:
        if type(data) in DataTypeTree.subclasses:
            return DataTypeTree.subclasses[type(data)]

        for subclass in DataTypeTree.subclasses.values():
            for wrap in subclass.wraps:
                if isinstance(data, wrap):
                    return subclass
        return DataTypeTree.subclasses[int]  # For instances created from any custom class.

    # TODO: Speed up
    def _check_tree_is_correct_one(self, data: object) -> None:
        wraps = self.wraps if isinstance(self.wraps, Iterable) else [self.wraps]
        if not any(isinstance(data, wraps_) for wraps_ in wraps):
            # if type(data) not in wraps:
            wraps_str = [element.__name__ for element in wraps]
            raise DataTypeTreeError(
                f"The given parser ({type(self).__name__}) is meant to parse `{', '.join(wraps_str)}` data type but "
                f"{type(data).__name__} was given"
            )

    def __pre_child_instantiation__(self) -> None:
        ...

    def __post_child_instantiation__(self) -> None:
        ...

    def _get_height(self) -> int:
        """Get maximum height of the current node in the tree."""
        max_height = 0
        for child in self:
            max_height = max(child.height, max_height)
        return max_height + 1

    @staticmethod
    def _validate_name(name: str) -> None:
        """CHeck that any given name is compatible with Python keyword naming rules."""
        if not is_string_python_keyword_compatible(name):
            raise DataTypeTreeError(f"The given name ({name}) is not Python-keyword compatible")

    @abstractmethod
    def _instantiate_children(self, data: object) -> Optional[ChildrenStructure[DataTypeTree]]:
        """Instantiate the child structure that will be assigned to `self.children`.

        This one will depend on how each subclass manage the child structure.
        """

    @final
    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Populate `subclasses` with all subclasses of this same class."""
        super().__init_subclass__(**kwargs)
        for type_ in cls.wraps:
            if type_ != object:
                if type_ in cls.subclasses:
                    raise DataTypeTreeError(f"A parser for {type_.__name__} was already found")
                cls.subclasses[type_] = cls  # type: ignore

    @abstractmethod
    def _get_hash(self) -> Hashable:
        """Get a unique hash that identifies the current data type."""

    @final
    def __hash__(self) -> int:
        """Unique hash that identifies whether the current tree is considered to be unique."""
        if self._cached_hash is None:
            self._cached_hash = hash(self._get_hash())
        return self._cached_hash

    @abstractmethod
    def _get_str_top_node(self) -> str:
        """Get the type alias or the representation only for the current self.

        It does not include children.
        """

    @property
    def permission_to_be_created_as_type_alias(self) -> bool:
        """Parameter that indicates whether the current class is allowed to be created as a type alias.

        This will depend on the parsing strategy and on the fact that some trees require a type
        alias no matter its height.
        """
        if self.parent is None:
            return True
        return bool(self.height > self.strategies.min_height_to_define_type_alias)

    @final
    def get_str_top_node_without_lvalue(self) -> str:
        return self.get_str_top_node().split("=")[-1].strip()

    @final
    def get_str_top_node(self) -> str:
        return self._get_str_top_node()

    @final
    def get_str_all_nodes(self, include_imports: bool = True) -> str:
        """String that represents the .py file created from the tree."""
        return self._format_node_strings(self.get_strs_all_nodes_unformatted(include_imports=include_imports))

    @final
    @cache_returned_value
    def get_strs_all_nodes_unformatted(self, *, include_imports: bool = True) -> Tuple[str, ...]:
        """Get, ordered by dependencies, all strings representing the whole tree."""
        strings: OrderedSet[str] = OrderedSet()
        self._get_strs_all_nodes_unformatted(types=strings)
        strings_lst = strings.as_list()
        if include_imports:
            strings_lst.insert(0, self.imports.format())
        return tuple(strings_lst)

    @final
    def _get_strs_all_nodes_unformatted(self, *, types: Optional[OrderedSet[str]] = None) -> None:
        if types is None:
            types = OrderedSet()

        if self.depth == 0 and not self.children:
            if self.permission_to_be_created_as_type_alias:
                types.add(self.get_str_top_node())
            return
        if not self.children:
            return

        for child in self:
            child._get_strs_all_nodes_unformatted(types=types)
            if child.permission_to_be_created_as_type_alias:
                types.add(child.get_str_top_node())
        if self.permission_to_be_created_as_type_alias:
            types.add(self.get_str_top_node())
        return

    @final
    def _format_node_strings(self, strs_py: Sequence[str]) -> str:
        """Get the string representation of the type hints that represent the whole tree."""
        strs_py = list(strs_py)
        if not strs_py:
            return ""

        # Add extra separation between imports and first line
        for idx, line in enumerate(strs_py):  # noqa: B007
            if "" in line:
                break
        strs_py[idx] = strs_py[idx] + "\n"

        # 2 empty lines before defining a class
        for idx, line in enumerate(strs_py[2:], start=2):
            if line.startswith("class"):
                strs_py[idx] = "\n" + strs_py[idx]

        return "\n\n".join(strs_py)

    @final
    def __str__(self) -> str:
        """String that represents the .py file created from the tree."""
        return self.get_str_all_nodes(include_imports=True)

    @final
    def __repr__(self) -> str:
        return f"{type(self).__name__}-{self.name}"

    @abstractmethod
    def __iter__(self) -> Self:
        """Get an iterator to iterate over the children of the tree."""

    @final
    def __len__(self) -> int:
        """Number of children within the tree."""
        if self.children is None:
            return 0
        return len(self.children)

    @abstractmethod
    def __next__(self) -> DataTypeTree:
        """Iterate over the children of the tree."""

    @final
    def print_children(self) -> None:
        print(repr(self))

    @final
    def __eq__(self, other_object: object) -> bool:
        if type(self) is type(other_object):
            return hash(self) == hash(other_object)
        return False

    @final
    def rename(self, new_name: str) -> None:
        """Rename the current node and all its subsequent children."""
        self._rename(new_name, len_old_name=len(self.name))

    @final
    def _rename(self, new_name: str, *, len_old_name: int) -> None:
        """Rename the current node and all its subsequent children."""
        if self.children:
            for child in self:
                child._rename(new_name=new_name, len_old_name=len_old_name)
        if self.parent is not None:
            self.name = new_name + self.name[len_old_name:]
        else:
            self.name = new_name
