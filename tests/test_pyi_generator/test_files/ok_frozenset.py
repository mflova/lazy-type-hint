from dynamic_pyi_generator.pyi_generator import PyiGenerator

data = frozenset({1, 2, 3})
data = PyiGenerator().from_data(data, class_type="Example")
