# Live API


This API generates type hints and exports the results into a cache-based folder within
this package. Once the type hints are generated, this information becomes instantly
available for IDEs and type checkers. Unless the cache-based folder is deleted, the
generated type information can be reused at any time.

For more details on fine-tuning the type information, see
[Configuration](./configuration.md).

## How to use it?

Input data to be hinted can be provided either as a Python object or from a YAML file:

=== "From a Python object"

    ```py
    from lazy_type_hint import LazyTypeHintLive

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

    my_data_hinted = LazyTypeHintLive().from_data(my_data, class_name="MyData")
    ```

=== "From a YAML file"

    Keep in mind that when information is loaded from a YAML file, comments starting with
    `#` are parsed and used as docstrings for the corresponding data structures.

    ```py
    import yaml

    from lazy_type_hint import LazyTypeHint


    def yaml_file_loader(path: str) -> object:
        with open(path) as f:
            return yaml.load(f, Loader=yaml.SafeLoader)


    LazyTypeHint().from_yaml_file(
        yaml_file_loader,
        path="file.yaml",
        class_name="MyData",
        comments_are="side",
    ).to_file("my_data")
    ```

## What are some of its potential use-cases?

This is ideal for data exploratory analysis when the structure of the given data is not
well-defined. The corresponding type information can be interpreted by the IDE, which will
provide additional functionalities such as autocompletion.

## How does it work?

When the `Live API` is used:

1. The type information is generated just like with the `Standard API`. This type is
   identified by the literal provided in `class_name`.
2. The type information is stored in a temporary folder within the library's directory.
3. Stub-based files (`*.pyi`) are generated to overwrite the original interface and return
   a new type when the `class_name` matches the given identifier.

## How can I reset the cache-based folder?

It is as simple as doing:

```py
from lazy_type_hint import LazyTypeHintLive

LazyTypeHintLive.reset()
```

This will remove all cached interfaces so far.