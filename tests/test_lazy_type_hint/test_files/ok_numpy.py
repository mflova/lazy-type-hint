from lazy_type_hint import LazyTypeHintLive
import numpy as np

arr = np.array([1,2,3])
arr2 = LazyTypeHintLive().from_data(arr, class_name="Example")
arr2.dtype