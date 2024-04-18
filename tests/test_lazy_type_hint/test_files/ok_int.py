from lazy_type_hint import LazyTypeHintLive

num: float = 2.0
num = LazyTypeHintLive().from_data(num, class_name="Example")
