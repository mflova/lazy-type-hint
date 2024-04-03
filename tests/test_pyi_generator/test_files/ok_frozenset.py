from lazy_type_hint.lazy_type_hint import LazyTypeHint

data = frozenset({1, 2, 3})
data = LazyTypeHint().from_data(data, class_name="Example")
