# TODO

1. Make `data = LazyTypeHintLive().from_data(data)` not throw any static type error. This
   happens because the new class created has nothing to do with original `data`. However,
   if the new class is created inhering from data, that assignment will not throw any
   error. For this, for the most bottom class that you defined, instead of doing this:

   ```py
   # More nested classes here

   A = List[str]
   ```

   Do this
    
    ```py
    # More nested classes here

    class A(List[str]):
        ...
    ```