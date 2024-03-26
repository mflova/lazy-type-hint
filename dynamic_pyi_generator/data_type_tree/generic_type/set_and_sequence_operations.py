"""This module groups common operations that are applied to both sets and sequences.

Although they present a total different behaviour at runtime, from the point of view of type
hinting they are quite similar.
"""

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    List,
    Sequence,
    Set,
    Tuple,
    Union,
    cast,
)

from dynamic_pyi_generator.data_type_tree.factory import data_type_tree_factory
from dynamic_pyi_generator.data_type_tree.generic_type.dict_data_type_tree import DictDataTypeTree

if TYPE_CHECKING:
    from dynamic_pyi_generator.data_type_tree.data_type_tree import DataTypeTree
    from dynamic_pyi_generator.data_type_tree.generic_type.sequence_data_type_tree import SequenceDataTypeTree
    from dynamic_pyi_generator.data_type_tree.generic_type.set_data_type_tree import SetDataTypeTree


@dataclass(frozen=True)
class SetAndSequenceOperations:
    data_type_tree: "Union[SetDataTypeTree, SequenceDataTypeTree]"

    def instantiate_childs(self, data: Sequence[Any], *, allow_repeated_childs: bool) -> Tuple["DataTypeTree", ...]:
        """Instantiate the childs for sets and sequences.

        If `allow_repeated_childs` is set to True, all childs will be returned even if they are repeated.
        """
        if allow_repeated_childs:
            childs: Union[Set[DataTypeTree], List[DataTypeTree]] = []
        else:
            childs = set()
        names_added: Set[str] = set()

        for element in data:
            name = f"{self.data_type_tree.name}{type(element).__name__.capitalize()}"
            # Generate new name in case this one was already added
            if name in names_added:
                modified_name = name
                count = 2
                while modified_name in names_added:
                    modified_name = f"{name}{count}"
                    count += 1
                name = modified_name
            child = data_type_tree_factory(
                data=element,
                name=name,
                imports=self.data_type_tree.imports,
                depth=self.data_type_tree.depth + 1,
                parent=self.data_type_tree,
                strategies=self.data_type_tree.strategies,
            )
            if allow_repeated_childs:
                childs = cast("List[DataTypeTree]", childs)
                childs.append(child)
                names_added.add(name)
            else:
                childs = cast("Set[DataTypeTree]", childs)
                if child in childs and isinstance(child, DictDataTypeTree) and child.dict_metadata.is_typed_dict:
                    self._update_existing_typed_dict_child_from_another_equal_child(childs, child)
                if child not in childs:
                    childs.add(child)
                    names_added.add(name)

        return self._merge_similar_typed_dicts(
            childs,
            merge_if_similarity_above=self.data_type_tree.strategies.merge_different_typed_dicts_if_similarity_above,
            allow_repeated_childs=allow_repeated_childs,
        )

    def _update_existing_typed_dict_child_from_another_equal_child(
        self, childs: "Iterable[DataTypeTree]", child: DictDataTypeTree
    ) -> None:
        """
        Merge dicts equal from the point of view of types but that might carry any extra information or metadata.

        This extra information can be hidden docstrings. Therefore, this will transfer all the information
        to the already added DictDataTypeTree child
        """
        for child_added in childs:
            if child == child_added and isinstance(child_added, DictDataTypeTree):
                child_added.update_data_and_metadata(child)

    @staticmethod
    def _merge_similar_typed_dicts(
        childs: "Union[Set[DataTypeTree], Sequence[DataTypeTree]]",
        *,
        merge_if_similarity_above: int,
        allow_repeated_childs: bool,
    ) -> "Tuple[DataTypeTree, ...]":
        """Merge similar TypedDicts.

        Only those TypedDict based childs are taken into account. If the similarity is above the expected one,
        a new child that contains a merged dictionary with the merged metadata is created. Then, all those TypedDict
        based childs are replaced within `childs` by the newly created merged child.
        """
        comparison = DictDataTypeTree.compare_multiple_typed_dicts_based_trees(*childs)
        if comparison.percentage_similarity < merge_if_similarity_above:
            return tuple(childs)
        if not comparison.all_corresponding_value_types_are_same_type:
            return tuple(childs)

        dict_data_type_trees: List[DictDataTypeTree] = []
        if allow_repeated_childs:
            childs = list(childs)
            for child in list(childs):
                if isinstance(child, DictDataTypeTree) and child.dict_metadata.is_typed_dict:
                    dict_data_type_trees.append(child)
            merged_child = DictDataTypeTree.from_multiple_dict_data_type_trees(*dict_data_type_trees)
            for idx, child in enumerate(childs):
                if isinstance(child, DictDataTypeTree) and child.dict_metadata.is_typed_dict:
                    childs[idx] = merged_child
            return tuple(childs)
        else:
            childs = cast("Set[DataTypeTree]", childs)
            for child in childs.copy():
                if isinstance(child, DictDataTypeTree) and child.dict_metadata.is_typed_dict:
                    childs.remove(child)
                    dict_data_type_trees.append(child)

            merged_child = DictDataTypeTree.from_multiple_dict_data_type_trees(*dict_data_type_trees)
            childs.add(merged_child) if isinstance(childs, list) else childs.add(merged_child)
            return tuple(childs)
