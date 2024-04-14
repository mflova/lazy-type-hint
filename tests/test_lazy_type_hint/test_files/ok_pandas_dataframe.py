from lazy_type_hint import LazyTypeHintLive
import pandas as pd

df = pd.DataFrame({"a": [1,2,3]})
data = LazyTypeHintLive().from_data(df, class_name="Example")
data["a"]

df = pd.DataFrame({("a", "b"): [1,2,3], ("a", "c"): [1,2,3]})
data = LazyTypeHintLive().from_data(df, class_name="Example2")
data["a"]
data["a"]["b"]
data["a"]["c"]
