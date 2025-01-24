# Configuration

Although `lazy-type-hint` works seamlessly without any additional configuration, the tool
offers a variety of parameters for fine-tuning type hint generation. These parameters can
be passed to the initializer of both `LazyTypeHint` and `LazyTypeHintLive` via the
ParsingStrategies class:

```py
from lazy_type_hint import LazyTypeHintLive, ParsingStrategies

obj = [1, 2, 3]
obj_type_hinted =  LazyTypeHintLive(ParsingStrategies()).from_data(obj, class_name="MyData")
```
## List Strategy

It can be set as: 

=== "List"

    Standard approach. Lists will be all hinted as `list[<types>]`

    ```py
    from lazy_type_hint import LazyTypeHint, ParsingStrategies

    obj = [1, 2, 3]
    lazy_type_hint =  LazyTypeHint(ParsingStrategies(list_strategy="list"))
    print(lazy_type_hint.from_data(obj, class_name="MyData").to_string(include_imports=False))

    # MyData: TypeAlias = list[int]
    ```

=== "Sequence"

    Lists will be all hinted as `Sequence[<types>]`. It can be helpful since
    `Sequence` is immutable and hence covariant.

    ```py
    from lazy_type_hint import LazyTypeHint, ParsingStrategies

    obj = [1, 2, 3]
    lazy_type_hint =  LazyTypeHint(ParsingStrategies(list_strategy="Sequence"))
    print(lazy_type_hint.from_data(obj, class_name="MyData").to_string(include_imports=False))

    # MyData: TypeAlias = Sequence[int]
    ```

## Tuple Size Strategy


=== "Fixed"

    ```py
    from lazy_type_hint import LazyTypeHint, ParsingStrategies

    obj = (1, "a")
    lazy_type_hint =  LazyTypeHint(ParsingStrategies(tuple_size_strategy="fixed"))
    print(lazy_type_hint.from_data(obj, class_name="MyData").to_string(include_imports=False))

    # MyData: TypeAlias = tuple[int, str]
    ```

=== "Any size"

    ```py
    from lazy_type_hint import LazyTypeHint, ParsingStrategies

    obj = (1, "a")
    lazy_type_hint =  LazyTypeHint(ParsingStrategies(tuple_size_strategy="any size"))
    print(lazy_type_hint.from_data(obj, class_name="MyData").to_string(include_imports=False))

    # MyData: TypeAlias = tuple[Union[int, str], ...]
    ```

## Dict strategy

=== "Dict"

    ```py
    from lazy_type_hint import LazyTypeHint, ParsingStrategies

    dct = {"name": "Albert", "age": 22}
    lazy_type_hint =  LazyTypeHint(ParsingStrategies(dict_strategy="dict"))
    print(lazy_type_hint.from_data(dct, class_name="MyData").to_string(include_imports=False))

    # MyData: TypeAlias = dict[str, Union[int, str]]
    ```

=== "Mapping"

    ```py
    from lazy_type_hint import LazyTypeHint, ParsingStrategies

    dct = {"name": "Albert", "age": 22}
    lazy_type_hint =  LazyTypeHint(ParsingStrategies(dict_strategy="Mapping"))
    print(lazy_type_hint.from_data(dct, class_name="MyData").to_string(include_imports=False))

    # MyData: TypeAlias = Mapping[str, Union[int, str]]
    ```

=== "TypedDict"

    ```py
    from lazy_type_hint import LazyTypeHint, ParsingStrategies

    dct = {"name": "Albert", "age": 22}
    lazy_type_hint =  LazyTypeHint(ParsingStrategies(dict_strategy="TypedDict"))
    print(lazy_type_hint.from_data(dct, class_name="MyData").to_string(include_imports=False))

    # class MyData(TypedDict):
    #     name: str
    #     age: int
    ```

## Pandas strategy

Type hinting `Pandas` objects can be challenging. To address this, three modes are
available:

=== "Do not type hint columns"

    ...

=== "Type hint only for autocomplete"

    ...

=== "Full type hint"

    ...


## Minimum depth to define type alias

type alias. This parameter defines the minimum depth a type must have to be defined as a
separate type alias.

```py
from lazy_type_hint import LazyTypeHint, ParsingStrategies

obj = [22, 23, ["Apple", "Banana"]]

lazy_type_hint =  LazyTypeHint(ParsingStrategies(min_depth_to_define_type_alias=2))
print(lazy_type_hint.from_data(obj, class_name="MyData").to_string(include_imports=False))

# MyData: TypeAlias = list[Union[int, list[str]]]


lazy_type_hint =  LazyTypeHint(ParsingStrategies(min_depth_to_define_type_alias=0))
print(lazy_type_hint.from_data(obj, class_name="MyData").to_string(include_imports=False))

# MyDataList: TypeAlias = list[str]
# MyData: TypeAlias = list[Union[MyDataList, int]]
```


## Key used as doc

Certain map-based data structures, especially those derived from JSON files, may include
embedded documentation within a reserved keyword. This can be specified using the
`key_used_as_doc` parameter. The example below demonstrates how the docstring is attached to
the `TypedDict` definition:

```py
from lazy_type_hint import LazyTypeHint, ParsingStrategies

obj = {"value": 2, "doc": "This is documentation"}

lazy_type_hint =  LazyTypeHint(ParsingStrategies(key_used_as_doc="doc"))
print(lazy_type_hint.from_data(obj, class_name="MyDict").to_string(include_imports=False))

# class MyDict(TypedDict):
#     """This is documentation."""
#
#     value: int
#     doc: str
```

## Merge different typed dicts if similarity is above

When loading data from YAML files, it is common to encounter list-based structures
containing multiple dictionaries. Some dictionaries may have optional or missing keys,
making it challenging for the algorithm to determine whether they should be declared as
separate dictionaries. During the merging process, keys not present in all dictionaries
are labeled as `NotRequired`. Lowering this parameter's value increases the likelihood of
dictionaries being merged.

```py
from lazy_type_hint import LazyTypeHint, ParsingStrategies

dct1 = {"name": "Joan", "age": 22}
dct2 = {"name": "Jule", "age": 19, "children": 2}
obj = [dct1, dct2]

lazy_type_hint =  LazyTypeHint(ParsingStrategies(merge_different_typed_dicts_if_similarity_above=99))
print(lazy_type_hint.from_data(obj, class_name="MyDict").to_string(include_imports=False))

# class MyDictDict2(TypedDict):
#     name: str
#     age: int
#     children: int
# 
# class MyDictDict(TypedDict):
#     name: str
#     age: int
# 
# MyDict: TypeAlias = list[Union[MyDictDict, MyDictDict2]]



lazy_type_hint =  LazyTypeHint(ParsingStrategies(merge_different_typed_dicts_if_similarity_above=30))
print(lazy_type_hint.from_data(obj, class_name="MyDict").to_string(include_imports=False))

# class MyDictDict(TypedDict):
#   name: str
#   age: int
#   children: NotRequired[int]
#
# MyDict: TypeAlias = list[MyDictDict]
```

## Typed dict read only values

=== "False"

    ```py
    from lazy_type_hint import LazyTypeHint, ParsingStrategies

    obj = {"name": "Joan", "age": 22}

    lazy_type_hint =  LazyTypeHint(ParsingStrategies(typed_dict_read_only_values=False))
    print(lazy_type_hint.from_data(obj, class_name="MyDict").to_string(include_imports=False))

    # class MyDict(TypedDict):
    #     name: str
    #     age: int
    ```

=== "True"

    ```py
    from lazy_type_hint import LazyTypeHint, ParsingStrategies

    obj = {"name": "Joan", "age": 22}

    lazy_type_hint =  LazyTypeHint(ParsingStrategies(typed_dict_read_only_values=True))
    print(lazy_type_hint.from_data(obj, class_name="MyDict").to_string(include_imports=False))

    # class MyDict(TypedDict):
    #     name: NotRequired[str]
    #     age: NotRequired[int]
    ```

## Check maximum n elements within container

To generate type hints for containers, the tool needs to analyze the types of all elements
within the container. This can be computationally expensive for containers with a large
number of elements. To reduce computation time, you can lower the
`check_max_n_elements_within_container` parameter. However, reducing it too much might
result in incorrect type hints:

```py
from lazy_type_hint import LazyTypeHint, ParsingStrategies

obj = [0, 1, "str"]

lazy_type_hint =  LazyTypeHint(ParsingStrategies(check_max_n_elements_within_container=1))
print(lazy_type_hint.from_data(obj, class_name="MyList").to_string(include_imports=False))

# MyList: TypeAlias = list[int]
```