# LazyTypeHint

<!---
Badge generated with:

```
python -c "import anybadge; anybadge.Badge('Python', '3.9 | 3.10 | 3.11 | 3.12', default_color='#14151a').write_badge('docs/images/pybadge.svg')"
```
-->

![Image](./images/pybadge.svg)

Quickly generate accurate ready-to-use type hints for any Python data structure.
`LazyTypeHint` supports a wide range of data types including dictionaries, callables,
Pandas DataFrames, numpy arrays, YAML files and more.

## Rationale

After long time working in the robotics industry and with large teams, I had to deal with
many configuration files. Each one of them with its own underlying data structures.
Working with them was not that easy:

- Since the IDE has not prior knowledge about the data structure, you will be coding
  "blind". None of the modern *Language Serve Protocol* (LSP) features integrated within an
  IDE such as IDE autocompletion or type checking will work
- Previous issue can be fixed by creating corresponding type hints that define the
  structure of the data. However, this was most of the times not possible:
    - Time consuming: What happens if the underlying data structure has to be extracted from
      a 10.000 lines YAML file?
    - Hard to maintain: Fixed type hint information can be hard to maintain. Any single
      change into the data structure has to be properly informed within the team so that
      corresponding data structure can be updated, which can be a source of bugs in the long
      term.
    - Even if one data structure is fully type hinted, how can I check that two data
      structures are sharing the same structure?

This tool aims to tackle this problem by generating type information that describes the
underlying data structure. This type information is exported as a normal Python module so
that you can benefit from any IDEs, type checkers or git-based features. A quick example
is shown below:

![Image](./images/example_from_data.PNG)


## Philosophy

What are the main set of characteristics that define the tool?

- **Quick**: Underlying algorithm can type hint data structures defined in thousand of
  lines almost instantaneously.
- **Efficient**: Detect equivalent "nodes" within the data structure to simplify the creation
  of type hints.
- **Ease of use**: Type hint any data structure in a single line.
- **IDE autocompletion and type checking**: Instantly provide useful meaningul information to
  IDEs and type checkers in order to 1) easily access the data structure and 2) perform
  static-based validation.
- **High degree of customization**: this allows the fine tuning for better type hint generation.
- **Immutability**: Type hint generation will not alter the input data.
- **Lightweight**: Only `typing_extensions` is required as dependency due to backwards
  compatibility reasons.

## Installation

Use any of your prefered package manager:

```
pip install lazy-type-hint
```

## API

The user can interact with the type hint generation via two main APIs:


=== "Standard API"

    Generate type hints that can be exported in a single file that can be later used and
    imported within your Python scripts. Ideal when type hints need to persist as a file
    within a git repository. See [Standard API](user_guide/standard_api.md) for more
    information.

    ```py
    from lazy_type_hint import LazyTypeHint, LazyTypeHintLive

    data = ({"name": "Peter", "age": 22},) # (1)!
    LazyTypeHint().from_data(data, class_name="MyData").to_file("file.py") # (2)!
    ```

    1. Any data structure that needs to be type hinted
    2. `LazyTypeHint` will generate a script `file.py` where you can export `MyData` type alias from.

=== "Live API"
    Generate type hints that are temporarily cached. Ideal for temporary data
    exploration. See [Lazy API](user_guide/live_api.md) for more information.

    ```py
    from lazy_type_hint import LazyTypeHint, LazyTypeHintLive

    data = ({"name": "Peter", "age": 22},) # (1)!
    data_type_hinted = LazyTypeHintLive().from_data(data, class_name="MyData") # (2)!
    ```

    1. Any data structure that needs to be type hinted
    2. After calling the script, output variable will contain the same data but will be fully type hinted