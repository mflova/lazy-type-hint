from lazy_type_hint import LazyTypeHintLive

num: int = 2
data = LazyTypeHintLive().from_data(num, class_name="Example")
