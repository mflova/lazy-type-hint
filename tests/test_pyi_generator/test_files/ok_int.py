from lazy_type_hint.lazy_type_hint import LazyTypeHint

num: float = 2.0
data = LazyTypeHint().from_data(num, class_name="Example")
