from dynamic_pyi_generator.pyi_generator import PyiGenerator

num: int = 2
data = PyiGenerator().from_data(num, class_name="Example")
