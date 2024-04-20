from typing import (
    Dict,
    Final,
    Hashable,
    List,
    Mapping,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

import pandas as pd
from typing_extensions import override

from lazy_type_hint.data_type_tree import data_type_tree_factory
from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
from lazy_type_hint.data_type_tree.generic_type.mapping_data_type_tree import MappingDataTypeTree
from lazy_type_hint.utils.utils import cache_returned_value_per_instance

LITERAL_OVERLOAD_TEMPLATE: Final = """    @overload  # type: ignore
    def __getitem__(self, key: Literal[{literal}]) -> {rtype}:
        ...
"""
OVERLOAD_TEMPLATE: Final = """    @overload  # type: ignore
    def __getitem__(self, key: {input_type}) -> {rtype}:
        ...
"""
TEMPLATE: Final = """class {class_name}(pd.DataFrame):

{overloads}
    @overload
    def __getitem__(
        self,
        key: Union[
            "pd.Series[bool]",
            {allowed_types},
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
            {allowed_types},
            pd.DataFrame,
            pd.Index,
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)"""

TEMPLATE_NO_PD: Final = """class {class_name}(pd.DataFrame):

{overloads}
    def __getitem__(
        self,
        key: Union[
            {allowed_types},
            npt.NDArray[np.bool_],
            npt.NDArray[np.str_],
            List[Union[Scalar, Tuple[Hashable, ...]]],
        ],
    ) -> Union[pd.Series, pd.DataFrame]:
        return super().__getitem__(key)"""


class PandasDataFrameDataTypeTree(MappingDataTypeTree):
    wraps = (pd.DataFrame,)
    data: pd.DataFrame
    children: Mapping[str, DataTypeTree]  # type: ignore[assignment]

    @override
    @property
    @cache_returned_value_per_instance
    def permission_to_be_created_as_type_alias(self) -> bool:
        """
        Set the permissions of this class to be created as a type alias.

        Situations where permission is given:
            - If columns are tuples: And first level are str, int or bool
            - If columns are not tuples: And columns are str, int, bool

        Otherwise delegate to super class
        """
        if all(isinstance(column, tuple) for column in self.data.columns):
            if all(isinstance(column[0], (str, bool, int)) for column in self.data.columns):
                return True
        else:
            if all(isinstance(column, (str, bool, int)) for column in self.data.columns):
                return True
        return super().permission_to_be_created_as_type_alias

    @property
    @cache_returned_value_per_instance
    def can_be_accessed_multilevel(self) -> bool:
        return self.all_columns_are(tuple)

    @property
    def are_column_same_type(self) -> bool:
        return len({type(column) for column in self.data.columns}) == 1

    def all_columns_are(self, type_: Type[object]) -> bool:
        return all(isinstance(column, type_) for column in self.data.columns)

    @property
    def are_columns_either_all_str_or_all_tuple(self) -> bool:
        if self.are_column_same_type:
            return all(isinstance(column, (str, int, tuple)) for column in self.data.columns)
        return False

    def _create_child(self, column: Hashable) -> DataTypeTree:
        suffix = self._to_camel_case(str(column))
        return data_type_tree_factory(  # type: ignore
            data=self.data[column],
            name=f"{self.name}{suffix}",
            imports=self.imports,
            depth=self.depth + 1,
            strategies=self.strategies,
            parent=self,
        )

    @override
    def _instantiate_children(self, data: pd.DataFrame) -> Mapping[Hashable, DataTypeTree]:
        children: Dict[Hashable, DataTypeTree] = {}
        if not self.are_columns_either_all_str_or_all_tuple:
            return {}

        # Corner case to avoid infinite recursion
        if all(isinstance(column, tuple) and len(column) == 1 for column in self.data.columns):
            return {}

        for column in data.columns:
            if not self.can_be_accessed_multilevel:  # Here all columns will  be Hashable
                column = cast(Hashable, column)
                children[column] = self._create_child(column)
            else:  # Here all columns will be tuple
                multi_column = cast(Tuple[Hashable, ...], column)
                columns_processed: Set[Union[bool, str, int]] = set()
                if multi_column[0] not in columns_processed:
                    if isinstance(multi_column[0], (str, int, bool)):
                        columns_processed.add(multi_column[0])
                        children[column[0]] = self._create_child(column[0])
        return children

    @override
    def _get_hash(self) -> str:
        if self.strategies.pandas_strategies == "Do not type hint columns":
            return "pd.DataFrame"
        return str(self.data.columns)

    @override
    def _get_str_top_node(self) -> str:
        self.imports.add("pandas")
        if len(self) == 0 or not self.strategies.pandas_strategies:
            self.imports.add("TypeAlias")
            return f"{self.name}: TypeAlias = pd.DataFrame"
        self.imports.add("overload")
        self.imports.add("Union")
        self.imports.add("Literal")
        self.imports.add("npt")
        self.imports.add("tuple")
        self.imports.add("list")
        self.imports.add("Hashable")
        self.imports.add("numpy")
        self.imports.add("pd.Scalar")

        overloads: List[str] = []
        for literal, child in self.children.items():
            if child.permission_to_be_created_as_type_alias:
                overloads.append(LITERAL_OVERLOAD_TEMPLATE.format(literal=repr(literal), rtype=child.name))
            else:
                rtype = "pd.Series" if isinstance(self.data[literal], pd.Series) else "pd.DataFrame"
                overloads.append(LITERAL_OVERLOAD_TEMPLATE.format(literal=repr(literal), rtype=rtype))
        if self.strategies.pandas_strategies == "Full type hint":
            all_literals = ", ".join(repr(key) for key in self.children)
            allowed_types = f"Literal[{all_literals}]"
            template = TEMPLATE_NO_PD
        else:
            allowed_types = "str"
            template = TEMPLATE
        return template.format(class_name=self.name, overloads="\n".join(overloads), allowed_types=allowed_types)
