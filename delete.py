from typing import FrozenSet

from dynamic_pyi_generator.data_type_tree import DataTypeTree

a: FrozenSet[int] = {1, 2}

data = [1, 2, 3]
print(DataTypeTree.get_data_type_tree_for_type(type(data)))
