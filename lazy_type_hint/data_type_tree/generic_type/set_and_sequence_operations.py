"""This module groups common operations that are applied to both sets and sequences.

Although they present a total different behaviour at runtime, from the point of view of type
hinting they are quite similar.
"""

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Sequence,
    Set,
    Tuple,
    Union,
    cast,
)

from lazy_type_hint.data_type_tree.factory import data_type_tree_factory
from lazy_type_hint.data_type_tree.generic_type.dict_data_type_tree import DictDataTypeTree

if TYPE_CHECKING:
    from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.sequence_data_type_tree import SequenceDataTypeTree
    from lazy_type_hint.data_type_tree.generic_type.set_data_type_tree import SetDataTypeTree


@dataclass(frozen=True)
class SetAndSequenceOperations:
    data_type_tree: "Union[SetDataTypeTree, SequenceDataTypeTree]"

    def instantiate_children(self, data: Sequence[Any], *, allow_repeated_children: bool) -> Tuple["DataTypeTree", ...]:
        """Instantiate the children for sets and sequences.

        If `allow_repeated_children` is set to True, all children will be returned even if they are repeated.
        """
        if allow_repeated_children:
            children: Union[Set[DataTypeTree], List[DataTypeTree]] = []
        else:
            children = set()
        names_added: Dict[DataTypeTree, str] = {}  # Used to generate new and unique cnames in a quicker way.

        child: DataTypeTree
        for element in data:
            name = f"{self.data_type_tree.name}{type(element).__name__.capitalize()}"
            # Generate new name in case this one was already added
            if name in names_added.values():
                modified_name = name
                count = 2
                while modified_name in names_added.values():
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
            if allow_repeated_children:
                children = cast("List[DataTypeTree]", children)
                if child in names_added:
                    child.rename(names_added[child])
                children.append(child)
                names_added[child] = child.name
            else:
                children = cast("Set[DataTypeTree]", children)
                if child in children and isinstance(child, DictDataTypeTree) and child.dict_metadata.is_typed_dict:
                    self._update_existing_typed_dict_child_from_another_equal_child(children, child)
                if child not in children:
                    children.add(child)
                    names_added[child] = name

        return self._merge_similar_typed_dicts(
            children,
            merge_if_similarity_above=self.data_type_tree.strategies.merge_different_typed_dicts_if_similarity_above,
            allow_repeated_children=allow_repeated_children,
        )

    def _update_existing_typed_dict_child_from_another_equal_child(
        self, children: "Iterable[DataTypeTree]", child: DictDataTypeTree
    ) -> None:
        """
        Merge dicts equal from the point of view of types but that might carry any extra information or metadata.

        This extra information can be hidden docstrings. Therefore, this will transfer all the information
        to the already added DictDataTypeTree child
        """
        for child_added in children:
            if child == child_added and isinstance(child_added, DictDataTypeTree):
                child_added.update_data_and_metadata(child)

    @staticmethod
    def _merge_similar_typed_dicts(
        children: "Union[Set[DataTypeTree], Sequence[DataTypeTree]]",
        *,
        merge_if_similarity_above: int,
        allow_repeated_children: bool,
    ) -> "Tuple[DataTypeTree, ...]":
        """Merge similar TypedDicts.

        Only those TypedDict based children are taken into account. If the similarity is above the expected one,
        a new child that contains a merged dictionary with the merged metadata is created. Then, all those TypedDict
        based children are replaced within `children` by the newly created merged child.
        """
        comparison = DictDataTypeTree.compare_multiple_typed_dicts_based_trees(*children)
        if comparison.percentage_similarity < merge_if_similarity_above:
            return tuple(children)
        if not comparison.all_corresponding_value_types_are_same_type:
            return tuple(children)

        dict_data_type_trees: List[DictDataTypeTree] = []
        if allow_repeated_children:
            children = list(children)
            for child in list(children):
                if isinstance(child, DictDataTypeTree) and child.dict_metadata.is_typed_dict:
                    dict_data_type_trees.append(child)
            merged_child = DictDataTypeTree.from_multiple_dict_data_type_trees(*dict_data_type_trees)
            for idx, child in enumerate(children):
                if isinstance(child, DictDataTypeTree) and child.dict_metadata.is_typed_dict:
                    children[idx] = merged_child
            return tuple(children)
        else:
            children = cast("Set[DataTypeTree]", children)
            for child in children.copy():
                if isinstance(child, DictDataTypeTree) and child.dict_metadata.is_typed_dict:
                    children.remove(child)
                    dict_data_type_trees.append(child)

            merged_child = DictDataTypeTree.from_multiple_dict_data_type_trees(*dict_data_type_trees)
            children.add(merged_child) if isinstance(children, list) else children.add(merged_child)
            return tuple(children)
