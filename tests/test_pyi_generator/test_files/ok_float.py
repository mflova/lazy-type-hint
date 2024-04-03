from lazy_type_hint.lazy_type_hint import LazyTypeHint

num: int = 2
data = LazyTypeHint().from_data(num, class_name="Example")
