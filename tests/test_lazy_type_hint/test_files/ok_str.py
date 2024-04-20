from lazy_type_hint import LazyTypeHintLive

string = "string"
string = LazyTypeHintLive().from_data(string, class_name="Example")
