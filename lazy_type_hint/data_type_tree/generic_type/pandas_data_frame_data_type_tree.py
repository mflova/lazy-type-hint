from typing import (
    Final,
    Union,
    cast,
)
from collections.abc import Hashable, Mapping

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
            list[Union[Scalar, tuple[Hashable, ...]]],
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
            list[Union[Scalar, tuple[Hashable, ...]]],
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
            list[Union[Scalar, tuple[Hashable, ...]]],
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

    def all_columns_are(self, type_: type[object]) -> bool:
        return all(isinstance(column, type_) for column in self.data.columns)

    @property
    def literal_compatible_types(self) -> tuple[type[str], type[bool], type[int]]:
        return str, bool, int

    @property
    def are_all_columns_literal_compatible(self) -> bool:
        column: Hashable
        for column in self.data.columns:
            if isinstance(column, tuple):
                column = column[0]
            if not isinstance(column, self.literal_compatible_types):
                return False
        return True

    def _create_child(self, column: Hashable) -> DataTypeTree:
        suffix = self._to_camel_case(str(column))
        suffix = suffix if suffix else "WSpace"
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
        children: dict[Hashable, DataTypeTree] = {}
        if not self.are_all_columns_literal_compatible:
            return {}

        # Corner case to avoid infinite recursion
        if all(isinstance(column, tuple) and len(column) == 1 for column in self.data.columns):
            return {}

        columns_processed: set[Union[bool, str, int]] = set()
        for column in data.columns:
            if not self.can_be_accessed_multilevel:  # Here all columns will  be Hashable
                column = cast(Hashable, column)
                children[column] = self._create_child(column)
            else:  # Here all columns will be tuple
                multi_column = cast(tuple[Hashable, ...], column)
                if multi_column[0] not in columns_processed:
                    if isinstance(multi_column[0], self.literal_compatible_types):
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
        self.imports.add("Hashable")
        self.imports.add("numpy")
        self.imports.add("pd.Scalar")

        overloads: list[str] = []
        for literal, child in self.children.items():
            if isinstance(literal, self.literal_compatible_types):
                if child.permission_to_be_created_as_type_alias:
                    overloads.append(LITERAL_OVERLOAD_TEMPLATE.format(literal=repr(literal), rtype=child.name))
                else:
                    rtype = child.get_str_top_node_without_lvalue()
                    overloads.append(LITERAL_OVERLOAD_TEMPLATE.format(literal=repr(literal), rtype=rtype))
        if self.strategies.pandas_strategies == "Full type hint":
            literal_compatible_keys: list[str] = []
            extra_types = ""
            for key in self.children:
                if isinstance(key, self.literal_compatible_types):
                    literal_compatible_keys.append(repr(key))
                else:
                    self.imports.add("Hashable")
                    extra_types = ", Hashable"  # This can be more precise, but not supported yet
            all_literals = ", ".join(literal_compatible_keys)
            allowed_types = f"Literal[{all_literals}]" + extra_types
            template = TEMPLATE_NO_PD
        else:
            allowed_types = "str"
            template = TEMPLATE
        return template.format(class_name=self.name, overloads="\n".join(overloads), allowed_types=allowed_types)
