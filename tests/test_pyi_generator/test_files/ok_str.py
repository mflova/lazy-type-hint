from lazy_type_hint.lazy_type_hint import LazyTypeHint

string = "string"
data = LazyTypeHint().from_data(string, class_name="Example")
