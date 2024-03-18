from dynamic_pyi_generator.pyi_generator import PyiGenerator

lst = [[2, 3, 4], [1.0, 2.0]]

data = PyiGenerator().from_data(lst, class_name="Example")
