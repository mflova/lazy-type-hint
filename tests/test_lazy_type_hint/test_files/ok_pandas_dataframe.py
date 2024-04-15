from lazy_type_hint import LazyTypeHintLive, ParsingStrategies
import pandas as pd
from contextlib import suppress

df = pd.DataFrame({"a": [1,2,3]})
data = LazyTypeHintLive(ParsingStrategies(pandas_strategies="Full type hint")).from_data(df, class_name="Example")
data["a"]

df = pd.DataFrame({("a", "b"): [1,2,3], ("a", "c"): [1,2,3]})
data2 = LazyTypeHintLive(ParsingStrategies(pandas_strategies="Full type hint")).from_data(df, class_name="Example2")
data2["a"]
data2["a"]["b"]
data2["a"]["c"]

df = pd.DataFrame({("a", "b"): [1,2,3], ("a", "c"): [1,2,3]})
data3 = LazyTypeHintLive(ParsingStrategies(pandas_strategies="Type hint only for autocomplete")).from_data(df, class_name="Example3")
with suppress(KeyError):
    data3["v"]

df = pd.DataFrame({("a", "b"): [1,2,3], ("a", "c"): [1,2,3]})
data4 = LazyTypeHintLive(ParsingStrategies(pandas_strategies="Do not type hint columns")).from_data(df, class_name="Example4")
with suppress(KeyError):
    data4["v"]