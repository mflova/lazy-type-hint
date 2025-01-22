# Live API

This API performs the type hint generation and exports the results into a cache-based
folder. Once these type hints are generated, this information is instantly available for
IDEs and type checkers. Unless this cache-based folder is erased, generated type
information can be re-used at any time.

For more details about the fine-tuning of the type information, see
[Configuration](./configuration.md)

## How to use it?

Input data to be hinted can be given either as a Python object or from a yaml file:


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

Once the type information has been generated, we can import it and use it anywhere else
within our project:

## What are some of its potential use-cases?

This is ideal to work in data-exploratory analysis when the structure of the data given is
not properly defined. Corresponding type information can be interpreted by the IDE which
will give extra functionalities such as IDE autocompletion.

## How does it work?

When the `Live API` is used:

1. The type information is generated same as with the `Standard API`. This type is
   identified by the literal given in `class_name`.
2. This type information is stored under a temporary folder within this library directory.
3. Stub-based files (`*.pyi`) are generated to overwrite the original interface and return
   a new type when `class_name` is matching the identifier given.

## How can I reset the cache-based folder?

As simple as doing:

```py
from lazy_type_hint import LazyTypeHintLive

LazyTypeHintLive.reset()
```

This will remove all interfaces cached so far.