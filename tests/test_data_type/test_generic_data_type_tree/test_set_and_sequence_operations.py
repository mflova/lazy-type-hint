from typing import Final, Union
from collections.abc import Hashable, Mapping, Sequence

import pytest

from lazy_type_hint.data_type_tree.data_type_tree import DataTypeTree
from lazy_type_hint.data_type_tree.factory import data_type_tree_factory
from lazy_type_hint.data_type_tree.generic_type import DictDataTypeTree
from lazy_type_hint.data_type_tree.generic_type.dict_data_type_tree import KeyInfo
from lazy_type_hint.data_type_tree.generic_type.list_data_type_tree import ListDataTypeTree
from lazy_type_hint.data_type_tree.generic_type.set_and_sequence_operations import (
    SetAndSequenceOperations,
)


class TestTransferHiddenKeys:
    PREFIX: Final = DictDataTypeTree.hidden_keys_prefix

    @pytest.mark.parametrize(
        "tree, expected_dict",
        [
            (
                data_type_tree_factory([{"name": "Joan"}, {"name": "Joan"}], name="A"),
                {"name": "Joan"},
            ),
            (
                data_type_tree_factory([{"name": "Joan"}, {"name": "Joan", f"{PREFIX}name": "doc"}], name="A"),
                {"name": "Joan", f"{PREFIX}name": "doc"},
            ),
            (
                data_type_tree_factory([{"name": "Joan", f"{PREFIX}name": "doc"}, {"name": "Joan"}], name="A"),
                {"name": "Joan", f"{PREFIX}name": "doc"},
            ),
        ],
    )
    def test_integration(self, tree: DataTypeTree, expected_dict: object) -> None:
        assert len(tree) == 1
        assert expected_dict == next(iter(tree.children)).data  # type: ignore


class TestMergeSimilarTypedDicts:
    NAME: Final = "EXAMPLE"

    @pytest.mark.parametrize("allow_repeated_children", [True, False])
    @pytest.mark.parametrize(
        "children, expected_key_info",
        [
            (
                {
                    DictDataTypeTree({"name": "Joan"}, name=NAME),
                    DictDataTypeTree({"name": "Joan", "age": 22}, name=NAME),
                },
                {
                    "name": KeyInfo(name="name", required=True),
                    "age": KeyInfo(name="age", required=False),
                },
            ),
            (
                {
                    ListDataTypeTree([1, 2], name=NAME),
                    DictDataTypeTree({"name": "Joan"}, name=NAME),
                    DictDataTypeTree({"name": "Joan", "age": 22}, name=NAME),
                },
                {
                    "name": KeyInfo(name="name", required=True),
                    "age": KeyInfo(name="age", required=False),
                },
            ),
            (
                {
                    ListDataTypeTree([1, 2], name=NAME),
                    DictDataTypeTree({".name": "Joan"}, name=NAME),
                    DictDataTypeTree({".name": "Joan", "age": 22}, name=NAME),
                },
                {
                    ".name": KeyInfo(name=".name", required=True),
                    "age": KeyInfo(name="age", required=False),
                },
            ),
        ],
    )
    def test_merge_similar_typed_dicts(
        self,
        children: Union[set[DataTypeTree], Sequence[DataTypeTree]],
        expected_key_info: Mapping[Hashable, KeyInfo],
        allow_repeated_children: bool,
    ) -> None:
        # Setup
        non_dict_count_before = 0
        for tree in children:
            if not isinstance(tree, DictDataTypeTree):
                non_dict_count_before += 1

        # Function to test
        if allow_repeated_children:
            children = tuple(children)
        output = SetAndSequenceOperations._merge_similar_typed_dicts(
            children, merge_if_similarity_above=20, allow_repeated_children=allow_repeated_children
        )

        dict_count = 0
        non_dict_count_after = 0
        for idx, tree in enumerate(output):
            if not isinstance(tree, DataTypeTree):
                pytest.fail(f"Expect to have a tuple of {DataTypeTree.__name__} objects.")
            if isinstance(tree, DictDataTypeTree):
                dict_count += 1
                idx_dict = idx
            else:
                non_dict_count_after += 1
        # Asserts
        assert non_dict_count_after == non_dict_count_before
        if not allow_repeated_children:
            assert (
                1 == dict_count  # noqa: SIM300
            ), f"After the merge, it is expected to find a single object of type `{DictDataTypeTree.__name__}`. Found {output}"
        tree = output[idx_dict]
        if not isinstance(tree, DictDataTypeTree):
            raise ValueError(
                f"The child extracted to read its dictionary metadata must be {DictDataTypeTree.__name__} but "
                f"found: {type(tree).__name__}"
            )
        assert expected_key_info == tree.dict_metadata.key_info

    @pytest.mark.parametrize("allow_repeated_children", [True, False])
    @pytest.mark.parametrize(
        "children, expected_key_info",
        [
            (
                {
                    DictDataTypeTree({"name": "Joan"}, name=NAME),
                    DictDataTypeTree({"name": "Joan", "age": 22}, name=NAME),
                },
                {
                    "name": KeyInfo(name="name", required=True),
                    "age": KeyInfo(name="age", required=True),
                },
            ),
            (
                {
                    ListDataTypeTree([1, 2], name=NAME),
                    DictDataTypeTree({"name": "Joan"}, name=NAME),
                    DictDataTypeTree({"name": "Joan", "age": 22}, name=NAME),
                },
                {
                    "name": KeyInfo(name="name", required=True),
                    "age": KeyInfo(name="age", required=True),
                },
            ),
            (
                {
                    ListDataTypeTree([1, 2], name=NAME),
                    DictDataTypeTree({".name": "Joan"}, name=NAME),
                    DictDataTypeTree({".name": "Joan", "age": 22}, name=NAME),
                },
                {
                    ".name": KeyInfo(name="name", required=True),
                    "age": KeyInfo(name="age", required=True),
                },
            ),
            (
                {
                    ListDataTypeTree([1, 2], name=NAME),
                    DictDataTypeTree({}, name=NAME),
                    DictDataTypeTree({".name": "Joan", "age": 22}, name=NAME),
                },
                {
                    ".name": KeyInfo(name="name", required=True),
                    "age": KeyInfo(name="age", required=True),
                },
            ),
        ],
    )
    def test_not_merge_similar_typed_dicts(
        self,
        children: Union[set[DataTypeTree], Sequence[DataTypeTree]],
        expected_key_info: Mapping[Hashable, KeyInfo],
        allow_repeated_children: bool,
    ) -> None:
        # Setup
        trees_before = len(children)

        # Function to test
        output = SetAndSequenceOperations._merge_similar_typed_dicts(
            children, merge_if_similarity_above=99, allow_repeated_children=allow_repeated_children
        )

        assert len(output) == trees_before
        for tree in output:
            if isinstance(tree, DictDataTypeTree):
                for value in expected_key_info.values():
                    assert value.required, "If there is no merge, it is expected all keys are marked as required."
