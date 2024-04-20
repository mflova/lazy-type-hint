from lazy_type_hint import LazyTypeHintLive, ParsingStrategies
import pandas as pd
from contextlib import suppress

df = pd.DataFrame({("a", "b"): [1,2,3], ("a", "c"): [1,2,3]})
df = LazyTypeHintLive(ParsingStrategies(pandas_strategies="Full type hint")).from_data(df, class_name="Example2")
with suppress(KeyError):
    df["a"]["d"]
