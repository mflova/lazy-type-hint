from lazy_type_hint import LazyTypeHintLive, ParsingStrategies
import pandas as pd
from contextlib import suppress

df = pd.Series([1,2,3])
df = LazyTypeHintLive().from_data(df, class_name="Example")
for value in df:
    value + 2