from lazy_type_hint import LazyTypeHintLive
import pandas as pd
from contextlib import suppress

df = pd.DataFrame({("a", "b"): [1,2,3], ("a", "c"): [1,2,3]})
data = LazyTypeHintLive().from_data(df, class_name="Example2")
with suppress(KeyError):
    data["a"]["d"]
