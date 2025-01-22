# Standard API

This API performs the type hint generation and allows its export into standard `.py` files.

For more details about the fine-tuning of the type information, see
[Configuration](./configuration.md)

## How to use it?

Input data to be hinted can be given either as a Python object or from a yaml file:


=== "From a Python object"

    ```py
    from lazy_type_hint import LazyTypeHint

    my_data = (
        {
            "name": "Albert",
            "age": 22,
            "hobbies": ["swimming", "reading"],
            "children": {
                "name": "John"
            }
        },
        {
            "name": "Albert",
            "age": 22,
            "children": {
                "name": "John"
            }
        }
    )

    LazyTypeHint().from_data(my_data, class_name="MyData").to_file("my_data.py")
    ```

=== "From a YAML file"

    ```py
    import yaml

    from lazy_type_hint import LazyTypeHintLive


    def yaml_file_loader(path: str) -> object:
        with open(path) as f:
            return yaml.load(f, Loader=yaml.SafeLoader)


    yaml_content = LazyTypeHintLive().from_yaml_file(
        yaml_file_loader,
        path="file.yaml",
        class_name="MyData",
        comments_are="side",
    )
    ```

This will generate the following type interface called `MyData` under `my_data.py`:

```py
from typing import TypedDict
from typing_extensions import NotRequired, TypeAlias


class MyDataDictChildren(TypedDict):
    name: str


class MyDataDict(TypedDict):
    name: str
    age: int
    hobbies: NotRequired[list[str]]
    children: MyDataDictChildren

MyData: TypeAlias = tuple[MyDataDict, MyDataDict]
```

Hence this type information `MyData` can be used to type hint any data structure:

![Image](../images/example_standard_api.PNG)

## What are some of its potential use-cases?

- Data structure validation: Considering that the tool generates type information that
  defines the underlying structure, `Standard API` can also be used to export the results
  as a string and compare whether two objects share the same data structure while ignoring
  the change of its values.
- Static validation: Having type information about the data structure will allow type
  checkers to be more accurate and ensure type coherency along the data structure and its
  uses.
- Ease of development: Type information generated will be interpreted by the IDE. This
  will make accessing the structure way easier due to its autocompletion features.
- Data structure interface generation: Some data structures can be rather complex to type
  hint. Most of the times it takes long time. This tool will generate these interfaces in
  a matter of milliseconds.