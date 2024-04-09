from lazy_type_hint import LazyTypeHintLive

data = frozenset({1, 2, 3})
data = LazyTypeHintLive().from_data(data, class_name="Example")
