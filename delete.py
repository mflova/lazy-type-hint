from typing_extensions import ReadOnly, TypedDict

from dynamic_pyi_generator.pyi_generator import PyiGenerator

data = [[1, 2, 3], [1, 2, 4, 5]]
PyiGenerator().reset()
# a = PyiGenerator().from_data(data, class_name="Example")
