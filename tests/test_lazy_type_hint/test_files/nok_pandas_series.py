from lazy_type_hint import LazyTypeHintLive, ParsingStrategies
import pandas as pd
from contextlib import suppress

df = pd.Series([1,2,"a"])
df = LazyTypeHintLive().from_data(df, class_name="Example")
with suppress(TypeError):
    for value in df:
        value + 2