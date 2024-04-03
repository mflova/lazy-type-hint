from lazy_type_hint.lazy_type_hint import LazyTypeHint

lst = [[2, 3, 4], [1.0, 2.0]]

data = LazyTypeHint().from_data(lst, class_name="Example")
