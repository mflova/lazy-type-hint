from dynamic_pyi_generator.pyi_generator import PyiGenerator

num: float = 2.0
data = PyiGenerator().from_data(num, class_name="Example")
