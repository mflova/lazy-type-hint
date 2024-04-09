from lazy_type_hint import LazyTypeHintLive

lst = [[2, 3, 4], [1.0, 2.0]]

data = LazyTypeHintLive().from_data(lst, class_name="Example")
