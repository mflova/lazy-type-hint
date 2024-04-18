from lazy_type_hint import LazyTypeHintLive, ParsingStrategies
import pandas as pd
from contextlib import suppress

df = pd.DataFrame({"a": [1,2,3]})
df = LazyTypeHintLive(ParsingStrategies(pandas_strategies="Full type hint")).from_data(df, class_name="Example")
df["a"]

df2 = pd.DataFrame({("a", "b"): [1,2,3], ("a", "c"): [1,2,3]})
df2 = LazyTypeHintLive(ParsingStrategies(pandas_strategies="Full type hint")).from_data(df2, class_name="Example2")
df2["a"]
df2["a"]["b"]
df2["a"]["c"]

df3 = pd.DataFrame({("a", "b"): [1,2,3], ("a", "c"): [1,2,3]})
df3 = LazyTypeHintLive(ParsingStrategies(pandas_strategies="Type hint only for autocomplete")).from_data(df3, class_name="Example3")
with suppress(KeyError):
    df3["v"]

df4 = pd.DataFrame({("a", "b"): [1,2,3], ("a", "c"): [1,2,3]})
df4 = LazyTypeHintLive(ParsingStrategies(pandas_strategies="Do not type hint columns")).from_data(df4, class_name="Example4")
with suppress(KeyError):
    df4["v"]