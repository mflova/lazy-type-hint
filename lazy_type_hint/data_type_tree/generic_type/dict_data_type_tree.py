import keyword
from collections import defaultdict
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    Hashable,
    Iterable,
    KeysView,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Type,
    TypeVar,
    cast,
)

from typing_extensions import Self, TypeGuard, override

from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
from lazy_type_hint.data_type_tree.generic_type.mapping_data_type_tree import MappingDataTypeTree
from lazy_type_hint.strategies import ParsingStrategies
from lazy_type_hint.utils import TAB, format_string_as_docstring, is_string_python_keyword_compatible

ValueT = TypeVar("ValueT")


@dataclass(frozen=True)
class DictMetadataComparison:
    common_keys: Set[Hashable] = field(default_factory=set)
    non_common_keys: Set[Hashable] = field(default_factory=set)
    value_types: Mapping[Hashable, Set[Type[object]]] = field(default_factory=lambda: defaultdict(set))

    @property
    def percentage_similarity(self) -> int:
        total_keys = len(self.common_keys) + len(self.non_common_keys)
        if total_keys == 0:
            return 0
        return int(100 * (len(self.common_keys) / total_keys))

    @property
    def all_corresponding_value_types_are_same_type(self) -> bool:
        return all(len(value_types_) == 1 for value_types_ in self.value_types.values())


@dataclass
class KeyInfo:
    name: Hashable
    docstring: str = ""
    required: bool = True


class DictMetadata:
    """Represents the metadata of a dictionary data type."""

    hidden_key_prefix: str
    """Prefix prepended to a key to indicate this one should be hidden when building its type alias."""
    key_info: Dict[Hashable, KeyInfo]
    """Extra information associated to every key of the dictionary."""

    _data: Dict[Hashable, object]
    _strategies: ParsingStrategies
    _initial_keys: KeysView[Hashable]

    def __init__(
        self, data: Mapping[Hashable, object], *, hidden_key_prefix: str, strategies: ParsingStrategies
    ) -> None:
        self._data = dict(data)
        self._initial_keys = data.keys()
        self._strategies = strategies
        self.hidden_key_prefix = hidden_key_prefix
        self.key_info = {}
        self._update_key_info(force_all_required_to_true=True)

    def get_keys(self, *, include_hidden_prefix_keys: bool = False) -> Set[Hashable]:
        """Get all keys within the wrapped dictionary."""
        if include_hidden_prefix_keys:
            return set(self._data.keys())
        if self._all_keys_are_string(self._data):
            return {key for key in self._data if not key.startswith(self.hidden_key_prefix)}
        return set(self._data.keys())

    @staticmethod
    def compare_multiple_dicts(*dicts_metadata: "DictMetadata") -> DictMetadataComparison:
        """Compute different metrics between multiple metadata objects."""
        keys_per_dictionary = [set(object_.get_keys()) for object_ in dicts_metadata]
        if not keys_per_dictionary:
            return DictMetadataComparison()

        common_keys = set.intersection(*keys_per_dictionary)
        total_keys = set.union(*keys_per_dictionary)
        non_common_keys = total_keys - common_keys

        value_types: Dict[Hashable, Set[Type[object]]] = defaultdict(set)
        for dct in dicts_metadata:
            for key, value in dct._data.items():
                value_type = type(value)
                if value_type == float and int in value_types[key]:
                    value_types[key].remove(int)
                value_types[key].add(type(value))
        return DictMetadataComparison(common_keys=common_keys, non_common_keys=non_common_keys, value_types=value_types)

    @property
    def is_typed_dict(self) -> bool:
        if self._all_keys_are_string(self._data) and self._strategies.dict_strategy == "TypedDict":
            return True
        return False

    @property
    def is_functional_syntax(self) -> bool:
        if self._all_keys_are_string(self._data) and self._all_keys_are_parsable():
            return False
        return True

    @staticmethod
    def _all_keys_are_string(dct: Mapping[Hashable, ValueT]) -> "TypeGuard[Mapping[str, ValueT]]":
        return all(isinstance(key, str) for key in dct)

    def _all_keys_are_parsable(self) -> bool:
        if self._all_keys_are_string(self._data) and all(key not in keyword.kwlist for key in self._data):
            return all(is_string_python_keyword_compatible(key) for key in self._data)
        return False

    def update(self, other: "DictMetadata") -> Mapping[Hashable, object]:
        """Update the wrapped dictionary and its metadata by including a new metadata object."""
        for key, value in other._data.items():
            if key not in self._data:
                self._data[key] = value
        self._update_key_info(other._initial_keys)
        return self._data

    def _update_key_info(
        self, keys_that_were_introduced: Optional[KeysView[Hashable]] = None, force_all_required_to_true: bool = False
    ) -> None:
        """Update the key information within this dictionary.

        If `keys_that_were_introduced` is None, all keys will be assumed as `Required`. However, if this one is given,
        a comparison between the existing keys and the given ones is done in order to save which keys are required
        and which ones not.
        """
        docstrings = self.get_key_docstrings(docstring_keys_start_with=self.hidden_key_prefix)

        for key in self._data:
            if key not in self.key_info:
                if isinstance(key, str) and key.startswith(self.hidden_key_prefix):
                    continue
                if force_all_required_to_true:
                    self.key_info[key] = KeyInfo(name=key, required=True)
                else:
                    self.key_info[key] = KeyInfo(name=key, required=False)
            if key in docstrings:
                self.key_info[key].docstring = docstrings[key]

        if force_all_required_to_true:
            return

        if not keys_that_were_introduced:
            for key_info in self.key_info.values():
                key_info.required = False
            return

        non_required_key: Hashable
        for non_required_key in set.difference(set(self._initial_keys), keys_that_were_introduced):
            if isinstance(non_required_key, str) and non_required_key.startswith(self.hidden_key_prefix):
                continue
            self.key_info[non_required_key].required = False

    def get_key_docstrings(
        self, *, docstring_keys_start_with: str = "", return_formatted_as_docstring: bool = False
    ) -> Mapping[Hashable, str]:
        """Obtain a map that associates each key with its corresponding string.

        All those keys that do not have a docstring will not be present in this dictionary.
        """
        if not docstring_keys_start_with:
            docstring_keys_start_with = self.hidden_key_prefix
        if not self._all_keys_are_string(self._data):
            return {}
        dct: Dict[Hashable, str] = {}
        # Insert key docstrings
        for key in self._data:
            if not key.startswith(docstring_keys_start_with):  # Check key is not docstring based
                doc_key: str = f"{self.hidden_key_prefix}{key}"
                if doc_key in self._data:  # Check if there is key docstring
                    unformatted_docstring = self._data[doc_key]  # type: ignore
                    if not isinstance(unformatted_docstring, str):
                        continue
                    if return_formatted_as_docstring:
                        formated_docstring = (
                            "\n" + format_string_as_docstring(unformatted_docstring, indentation=TAB) + "\n"
                        )
                        dct[key] = formated_docstring
                    else:
                        dct[key] = unformatted_docstring
        return dct


class DictDataTypeTree(MappingDataTypeTree):
    wraps = (dict,)
    data: Dict[Hashable, object]
    dict_metadata: DictMetadata

    @staticmethod
    @override
    def _validate_name(name: str) -> None:
        """Removed name validation as the TypedDict can type any name."""
        return

    @override
    @property
    def permission_to_be_created_as_type_alias(self) -> bool:
        if self.dict_metadata.is_typed_dict:
            return True
        return super().permission_to_be_created_as_type_alias

    @override
    def __pre_child_instantiation__(self) -> None:
        self.dict_metadata = DictMetadata(
            self.data, hidden_key_prefix=self.hidden_keys_prefix, strategies=self.strategies
        )

    @override
    def _get_str_top_node(self) -> str:
        if self.dict_metadata.is_typed_dict:
            children_str_key = cast(Mapping[str, DataTypeTree], self.children)
            return self._parse_typed_dict(children=children_str_key)
        else:
            return self._parse_dict(self.children)

    def _parse_typed_dict(
        self,
        children: Mapping[str, DataTypeTree],
    ) -> str:
        """
        Define the name of the keys and values for the current dictionary.

        If the name of a child type alias needs to be created, this one will use as a suffix the name
        of the associated key.

        Example:
            - address: AddressList
            - age: AgeInt
        """
        self.imports.add("TypedDict")

        content: Dict[str, str] = {}
        for key, value in children.items():
            if isinstance(value, dict):
                type_value = f"{self.name}{self._to_camel_case(key)}"
                content[key] = type_value
            else:
                if not value.permission_to_be_created_as_type_alias:
                    content[key] = value.get_str_top_node_without_lvalue()
                else:
                    name = self._to_camel_case(value.name)
                    content[key] = name
                if key in self.dict_metadata.key_info:
                    if not self.dict_metadata.key_info[key].required:
                        self.imports.add("NotRequired")
                        content[key] = f"NotRequired[{content[key]}]"
                    if self.strategies.typed_dict_read_only_values:
                        self.imports.add("ReadOnly")
                        content[key] = f"ReadOnly[{content[key]}]"
        return self._build_typed_dict(
            name=self.name,
            content=content,
            functional_syntax=self.dict_metadata.is_functional_syntax,
            key_used_as_class_docstring=self.strategies.key_used_as_doc,
        )

    def _build_typed_dict(
        self,
        name: str,
        content: Mapping[str, str],
        *,
        functional_syntax: bool = False,
        key_used_as_class_docstring: str = "",
    ) -> str:
        """
        Build a typed dictionary based on the given name and content.

        Args:
            name (str): The name of the typed dictionary.
            content (Mapping[str, str]): The content of the typed dictionary, where each
                key-value pair represents a field and its type.
            functional_syntax (bool, optional): If True, use functional syntax to define
                the typed dictionary. Defaults to False.
            key_used_as_class_docstring (str, optional): The key to be used as the class docstring.
                This is a hidden one and it will not be represented in the final `TypedDict`.
                Defaults to an empty string.

        Returns:
            str: The string representation of the typed dictionary.
        """
        if functional_syntax:
            template = f"""{name} = TypedDict(
{TAB}"{name}",
{TAB}{{
{TAB}{TAB}"{{key}}": {{value}},
{TAB}}},
)"""
            idx_to_repeat = -3
        else:
            template = f"""class {name}(TypedDict):
{TAB}{{key}}: {{value}}{{optional_key_docstring}}"""
            idx_to_repeat = -1

        # Build the dictionary
        lines = template.splitlines()
        modified_line = ""
        key_docstrings = self.dict_metadata.get_key_docstrings(
            docstring_keys_start_with=self.hidden_keys_prefix, return_formatted_as_docstring=True
        )
        for key, value in content.items():
            if key.startswith(self.hidden_keys_prefix):  # Do not add artificially created keys
                continue
            if self.dict_metadata.is_functional_syntax:
                modified_line += lines[idx_to_repeat].format(key=key, value=value) + "\n"
            else:
                docstring = key_docstrings.get(key, "")
                modified_line += lines[idx_to_repeat].format(key=key, value=value, optional_key_docstring=docstring)
                if not docstring:
                    modified_line += "\n"
        lines[idx_to_repeat] = modified_line[:-1]

        # Append class docstring if found
        if key_used_as_class_docstring in self.data and key_used_as_class_docstring:
            lines = self._insert_class_docstring(lines, key_used_as_doc=key_used_as_class_docstring)
        return "\n".join(lines)

    def update_data_and_metadata(self, other: "DictDataTypeTree") -> None:
        """Given another child, this will update the current node with all the data and metadata."""
        self.data = dict(self.dict_metadata.update(other.dict_metadata))

    def _insert_class_docstring(self, lines: Sequence[str], *, key_used_as_doc: str) -> List[str]:
        string = self.data[key_used_as_doc]
        lines = list(lines)
        if isinstance(string, str):
            indentation = "" if self.dict_metadata.is_functional_syntax else TAB
            docstring = format_string_as_docstring(string, indentation=indentation)
            if self.dict_metadata.is_functional_syntax:
                lines.insert(len(lines), docstring)
            else:
                lines.insert(1, docstring + "\n")
        return lines

    @override
    def _get_hash(self) -> Hashable:
        if not self.dict_metadata.is_typed_dict:
            return super()._get_hash()
        hashes: List[object] = []
        for name, child in self.children.items():
            hashes.append(("typed_dict", name, child._get_hash()))
        return frozenset(hashes)

    @staticmethod
    def compare_multiple_typed_dicts_based_trees(*trees: "DictDataTypeTree") -> DictMetadataComparison:
        """
        Obtain metrics related to the comparison of multiple objects.

        This allows to check its similarity or keys in common for example.
        """
        dicts_metadata = [
            tree.dict_metadata
            for tree in trees
            if isinstance(tree, DictDataTypeTree) and tree.dict_metadata.is_typed_dict
        ]
        return DictMetadata.compare_multiple_dicts(*dicts_metadata)

    @classmethod
    def from_multiple_dict_data_type_trees(cls, *trees: "DictDataTypeTree") -> "Self":
        """
        Merge multiple dict data type trees.

        For thsis to happen, two main tasks are carried out:
            - Update `data` that holds the dictionary
            - Override `DictMetadata` with new information relative to all new information
        """
        merged_dict: Dict[Hashable, object] = {}
        for d in (tree.data for tree in trees):
            merged_dict.update(d)

        def check_same(trees: Iterable["DictDataTypeTree"], *, param: str) -> Any:
            if not trees:
                raise ValueError("At least one tree must be given")

            first_tree = next(iter(trees))
            if all(getattr(first_tree, param) == getattr(tree, param) for tree in trees):
                return getattr(first_tree, param)
            raise ValueError(f"Only {type(first_tree).__name__} with same `{param}` can be merged.")

        random_tree = next(iter(trees))
        shortest_name = ""
        for tree in trees:
            random_tree.dict_metadata.update(tree.dict_metadata)
            if not shortest_name:
                shortest_name = tree.name
            shortest_name = min(shortest_name, tree.name)

        new_tree = cls(
            data=merged_dict,
            name=shortest_name,
            imports=check_same(trees, param="imports"),
            depth=check_same(trees, param="depth"),
            strategies=check_same(trees, param="strategies"),
            parent=trees[0].parent,
        )
        new_tree.dict_metadata = random_tree.dict_metadata
        return new_tree
