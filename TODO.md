# TODO

- Refactor `__next__` of GenericType to be `abstractmethod`
- Fix: Pandas dataframe columns can be any other type than str (like int):
  - If the column is Hashable: Just type hint the type of the column
  - If the column is Hashable AND str/bool/int: Type hint Literal
- Fix: Fix cases where no string is returned:
- Feat: Return Narrow down Union[pd.Dataframe, pd.Series]

  ```py
    df = pd.DataFrame(({1: [1,2]}))
    tree = data_type_tree_factory(df, name="Example")
    print(tree.get_strs_all_nodes_unformatted(make_parent_class_inherit_from_original_type=False))
  ```

- Testing: Verify that `from_yaml` method does not modify the original dictionary
  contained in the yaml file.
- Testing: Write performance tests for pandas dataframe (deep columns, many columns...)
- Testing: Verify behaviour when the user has not `pandas` installed.