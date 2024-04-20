from lazy_type_hint import LazyTypeHintLive
from contextlib import suppress
import numpy as np

arr = np.array([1,2,3])
arr2 = LazyTypeHintLive().from_data(arr, class_name="Example")
with suppress(AttributeError):
    print(arr2.dttype)