from typing import Final

import pytest

from dynamic_pyi_generator.data_type_tree.simple_data_type_tree import SimpleDataTypeTree


class TestGetStrPy:
    NAME: Final = "Example"

    @pytest.mark.parametrize(
        "data, expected_str",
        [
            [range(1, 2), f"{NAME} = range"],
            [slice(1, 2), f"{NAME} = slice"],
            [True, f"{NAME} = bool"],
            [False, f"{NAME} = bool"],
            ["random_string", f"{NAME} = str"],
            [5, f"{NAME} = int"],
            [6.7, f"{NAME} = float"],
        ],
    )
    def test_get_str_py(self, data: object, expected_str: str) -> None:
        data_type_tree = SimpleDataTypeTree(data, self.NAME)
        assert expected_str == data_type_tree.get_str_py()
