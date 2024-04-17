# TODO

Performance:
- Refactor "operations" to be easier to understand. Probably move some of the operations
  into `TupleDataTypeTree`
    - This will reduce the number of branches within "operations" + easier to read
- Evaluate hash computation:
  - If it is retrieved multiple times due to recursion/trees, consider caching the value
- When creating new childs, check if `len(data)` is higher than a given number. If it is,
  check only first N first elements and assume all the other elements will be of same
  type.
- Improve `data_type_tree_factory` lookup:
  - Currently, many `isinstance` are being called. My proposal is to: 
    - Store data types in a dictionary. If it cannot be found via `type(my_data)` in
      `available_data_type_trees.subclasses`, find the one via `isinstance` check