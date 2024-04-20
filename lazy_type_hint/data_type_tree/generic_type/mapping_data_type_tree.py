import re
from collections import defaultdict
from typing import Dict, Final, Hashable, Iterator, List, Literal, Mapping, Set, Type

from typing_extensions import Self, override

from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
from lazy_type_hint.data_type_tree.factory import data_type_tree_factory
from lazy_type_hint.data_type_tree.generic_type.generic_data_type_tree import GenericDataTypeTree
from lazy_type_hint.file_modifiers.yaml_file_modifier import YamlFileModifier


class MappingDataTypeTree(GenericDataTypeTree):
    children: Mapping[Hashable, DataTypeTree]
    hidden_keys_prefix: Final = YamlFileModifier.prefix

    # Iterable-protocol related
    _keys: Iterator[Hashable]
    _iterator: Iterator[Hashable]

    @override
    def _instantiate_children(self, data: Mapping[Hashable, object]) -> Mapping[Hashable, DataTypeTree]:  # type: ignore
        children: Dict[Hashable, DataTypeTree] = {}
        children_info: Dict[DataTypeTree, Set[Hashable]] = defaultdict(set)

        for key, value in data.items():
            suffix = type(key).__name__ if not isinstance(key, str) else self._to_camel_case(key)
            if isinstance(key, str) and key.startswith(self.hidden_keys_prefix):
                continue
            child = data_type_tree_factory(
                data=value,
                name=f"{self.name}{suffix}",
                imports=self.imports,
                depth=self.depth + 1,
                strategies=self.strategies,
                parent=self,
            )
            children_info[child].add(key)
            children[key] = child
        self._assign_same_data_type_tree_to_keys_with_same_value_type(children, children_info=children_info)
        return children

    def _assign_same_data_type_tree_to_keys_with_same_value_type(
        self, children: Dict[Hashable, DataTypeTree], *, children_info: Dict[DataTypeTree, Set[Hashable]]
    ) -> None:
        """
        Simplify the tree.

        Find all values sharing the same data type tree, create a unique one and use this new one to replace all same
        values.
        """
        last_name_added: Dict[Type[object], int] = {}
        for data_type_tree, values in children_info.items():
            if len(values) > 1:  # Perform replacement if some values were detected to be the same in terms of types
                parent_name = data_type_tree.parent.name if data_type_tree.parent is not None else ""
                new_name = f"{parent_name}{data_type_tree.holding_type.__name__.capitalize()}"
                if data_type_tree.holding_type in last_name_added:
                    new_name += str(last_name_added[data_type_tree.holding_type] + 1)
                    last_name_added[data_type_tree.holding_type] += 1
                else:
                    last_name_added[data_type_tree.holding_type] = 1
                data_type_tree.rename(new_name)
                for hashable in values:
                    children[hashable] = data_type_tree

    def _get_str_top_node(self) -> str:
        return self._parse_dict(self.children)

    def _parse_dict(self, children: Mapping[Hashable, DataTypeTree]) -> str:
        """Get a string representation of the dictionary for this same top node.

        Examples:
            - Mapping[str, Union[float, str]]
            - Mapping[str, str]
        """
        container: Literal["dict", "TypedDict", "MappingProxyType", "Mapping"] = (
            "dict" if self.strategies.dict_strategy == "TypedDict" else self.strategies.dict_strategy
        )
        if self.holding_type.__name__ == "mappingproxy":
            container = "MappingProxyType"
            self.imports.add(container)
        else:
            self.imports.add(container)

        keys = self._get_types(iterable=children.keys(), remove_repeated=True)
        keys_str = self._format_types(keys)
        value_types = self.get_type_alias_children()

        container_ = "Dict" if container == "dict" else container
        return f"{self.name} = {container_}[{keys_str}, {value_types}]"

    @staticmethod
    def _to_camel_case(string: str) -> str:
        """Make it camel case and compatible with Python keywords."""
        # Remove any initial number within the string
        match = re.match(r"^\d+", string)
        if match:
            number = match.group()
            if not string[len(number) :]:
                return string
            string = string[len(number) :]

        new_string = [""] * len(string)
        idx_to_remove: Set[int] = set()
        removed = False
        for idx, char in enumerate(string):
            if not char.isalpha() and not char.isnumeric():
                idx_to_remove.add(idx)
            if idx not in idx_to_remove:
                if removed is True:
                    new_string[idx] = string[idx].upper()
                    removed = False
                else:
                    new_string[idx] = string[idx]
            else:
                removed = True

        try:
            new_string[0] = new_string[0].upper()
        except IndexError:
            return string
        return "".join(new_string)

    @override
    def _get_hash(self) -> Hashable:
        hashes: List[object] = []
        for name, child in self.children.items():
            hashes.append(("mapping", hash(type(name)), child._get_hash()))
        return frozenset(hashes)

    @override
    def __iter__(self) -> "Self":
        self._iterator = iter(self.children.keys())
        return self

    @override
    def __next__(self) -> DataTypeTree:
        key = next(self._iterator, None)
        if key is not None:
            return self.children[key]
        else:
            raise StopIteration
