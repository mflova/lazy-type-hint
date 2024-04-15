from typing import (
    Dict,
    Final,
    List,
    Mapping,
    Set,
    Type,
)

import pandas as pd
from typing_extensions import override

from lazy_type_hint.data_type_tree import data_type_tree_factory
from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
from lazy_type_hint.data_type_tree.generic_type.mapping_data_type_tree import MappingDataTypeTree

OVERLOAD_TEMPLATE: Final = """    @overload  # type: ignore
    def __getitem__(self, key: Literal["{literal}"]) -> {rtype}:
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
    wraps = pd.DataFrame
    data: pd.DataFrame
    children: Mapping[str, DataTypeTree]  # type: ignore[assignment]

    @override
    @property
    def permission_to_be_created_as_type_alias(self) -> bool:
        return bool(len(self) >= 1 and self.are_columns_either_all_str_or_all_tuple)

    @property
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
            return all(isinstance(column, (str, tuple)) for column in self.data.columns)
        return False

    def _create_child(self, column: str) -> DataTypeTree:
        suffix = self._to_camel_case(column)
        return data_type_tree_factory(  # type: ignore
            data=self.data[column],
            name=f"{self.name}{suffix}",
            imports=self.imports,
            depth=self.depth + 1,
            strategies=self.strategies,
            parent=self,
        )

    @override
    def _instantiate_children(self, data: Mapping[str, object]) -> Mapping[str, DataTypeTree]:  # type: ignore
        children: Dict[str, DataTypeTree] = {}
        if not self.are_columns_either_all_str_or_all_tuple:
            return children
        for column in self.data.columns:
            if not self.can_be_accessed_multilevel:  # Here all columns will  be str
                children[column] = self._create_child(column)
            else:  # Here all columns will be tuple
                columns_processed: Set[str] = set()
                for column in self.data.columns:
                    if column[0] not in columns_processed:
                        columns_processed.add(column[0])
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
                overloads.append(OVERLOAD_TEMPLATE.format(literal=literal, rtype=child.name))
            else:
                rtype = "Union[pd.DataFrame, pd.Series]"
                overloads.append(OVERLOAD_TEMPLATE.format(literal=literal, rtype=rtype))
        if self.strategies.pandas_strategies == "Full type hint":
            all_literals = ", ".join(f'"{key}"' for key in self.children)
            allowed_types = f"Literal[{all_literals}]"
            template = TEMPLATE_NO_PD
        else:
            allowed_types = "str"
            template = TEMPLATE
        return template.format(class_name=self.name, overloads="\n".join(overloads), allowed_types=allowed_types)
