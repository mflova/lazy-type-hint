# LazyTypeHint

Type hint any Python (nested) data structure! Dictionaries, callables, Pandas DataFrames...

```
pip install lazy-type-hint
```

## Quick examples

```py
from lazy_type_hint import LazyTypeHint, LazyTypeHintLive

data = [1,2,3]
LazyTypeHint().from_data(data, class_name="MyClass").to_file("file.py")
LazyTypeHint().from_data(data, class_name="MyClass").to_string()
data_type_hinted = LazyTypeHintLive().from_data(data, class_name="MyClass")
```

## Main features

1. Get corresponding type hints from any given data structure and with mutltiple parsing
   options. Export it as a file or as a string.

   ```py
      from lazy_type_hint import LazyTypeHint, ParsingStrategies

      # INPUT
      people = [
          {
              "name": "Peter",
              "age": 40,
              "kids": (
                  {
                      "name": "Peter Jr",
                      "age": 10,
                  },
                  {
                      "name": "Peter Jr2",
                      "age": 8,
                  },
              ),
          },
          {
              "name": "Kevin",
              "age": 42,
              "job": "Carpenter",
              "kids": (
                  {
                      "name": "Peter Jr",
                      "age": 10,
                  },
              ),
          },
      ]

      people_type_hint = (
          LazyTypeHint(
              strategies=ParsingStrategies(
                  min_height_to_define_type_alias=2,
                  tuple_size_strategy="any size",
              )
          )
          .from_data(people, class_name="People")
          .to_string()
      )
      print(people_type_hint)
   ```

   ```py
    # OUTPUT
    from typing import List, Tuple, TypedDict
    from typing_extensions import NotRequired


    class PeopleDictKidsDict(TypedDict):
        name: str
        age: int


    class PeopleDict(TypedDict):
        name: str
        age: int
        kids: Tuple[PeopleDictKidsDict, ...]
        job: NotRequired[str]

    People = List[PeopleDict]
   ```
2. [EXPERIMENTAL] Get type hints live with `LazyTypeHintLive`. The API changes its local
   interface as soon as you use it, allowing to automatically infer and reuse your type
   hints after executing your program once.

   |   Before executing the code    |   After executing the code    |
    |:-------------:|:-------------:|
    | ![Before executing the code](https://github.com/mflova/lazy-type-hint/blob/main/img/before.PNG?raw=true) | ![After executing the code](https://github.com/mflova/lazy-type-hint/blob/main/img/after.PNG?raw=true) |

    This will allow you to:

   |       |       |
    |:-------------:|:-------------:|
    | Perform static analysis to detect issues | ![After executing the code](https://github.com/mflova/lazy-type-hint/blob/main/img/errors.PNG?raw=true) |
    | Reuse your available type hints | ![After executing the code](https://github.com/mflova/lazy-type-hint/blob/main/img/reuse_classes.PNG?raw=true) |
    | Have full autocompletion support from your IDE | ![After executing the code](https://github.com/mflova/lazy-type-hint/blob/main/img/autocomplete.PNG?raw=true) |




3. Easily type hint your files (YAML, JSON) and parse extra comments found within this
   file as part of the type hint docstrings. Given a yaml file like:

   ```yaml
    # Collection of sensors
    sensors:
      - name: Sensor1
        # Type of sensor used
        sensor_type: Temperature
        location: Living Room
        # Maximum amount allowed.
        # NOTE: Only 3 are available
        threshold: 25  # Units: [C]

      - name: Sensor2
        sensor_type: Humidity
        location: Bedroom
        threshold: 60

      - name: Sensor3
        sensor_type: Pressure
        location: Kitchen
        threshold: 1000
   ```

   And the code:
   ```py
      from lazy_type_hint import LazyTypeHint


    def load_yaml_file(file_path):
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
        return data


    print(LazyTypeHint().from_yaml_file(
        loader=load_yaml_file,
        path="example.yaml",
        class_name="Sensors",
        comments_are=("above", "side"),
    ).to_string())
   ```

   Generate type hints like:

   ```py
   from typing import List, TypedDict


   class SensorsSensorsDict(TypedDict):
       name: str
       sensor_type: str
       """Type of sensor used. NOTE: Only 3 are available."""
       location: str
       threshold: int
       """
       Maximum amount allowed.

       Units: [C].
       """

   SensorsSensors = List[SensorsSensorsDict]


   class Sensors(TypedDict):
       sensors: SensorsSensors
       """Collection of sensors."""
   ```

## What makes it a different tool?

There are some tools that aim to perform something similar. `Cattrs` or `pydantic` require
knowing the structure beforehand. Then, the developer is responsible for writing it. They
are validation-oriented. This tool is more geared towards providing better type hints in
an automated way and ensuring that the structure is accessed correctly. Although other
tools such as `Stubgen` are able to generate `.pyi` files in an automated way, it might be
required to edit the environment to indicate where these stub-based files are located.

## All features

Main features:
 - Type hint any (nested) structure.
 - Validate structures by comparising its string representation via `LazyTypeHintLive`
 - Dictionaries can be type hinted as `TypedDict`, meaning that the IDE will have extra
   information about its underlying structures. Developer can therefore benefit from extra
   static analysis or autcomplete features.
 - Similarity based merge:
   - Equal (nested) structures will be detected as such and type hinted under the same type alias.
   - Similar structures such as dictionaries will be merged indicating which keys were
     found to be not mandatory or required.
 - Type hint structures within any given file (YAML, JSON...).
 - Document structures:
    - Specify a specific keyword within dictionaries that will be parsed and
      included as a docstring.
    - Some file format such as like YAML will also find and parse comments as docstrings.
 - Wide range of type hint based on strategies. The user can select at any time: 
   - Which kind of container is prefered (`Sequence`/`list`)
   - How to type hint a tuple (either with fixed or non-fixed size)
   - The complexity of the type aliases to be created.
   - Dictionaries typed as `Mapping`, `Dict` or `TypedDict`
   - Minimum percentage of similarity between dicts to be merged.
   - Mutable or read-only based `TypedDict`.
 
Structures that can be type hinted:
 - Sequences: list, tuples
 - Sets: sets, frozensets
 - Dictionaries: dict, MappingProxyType
 - Pandas DataFrame: Full support for string-based columns and `MultiIndex` columns
 - Simple built-in types: bool, int, float, range, slice, None, str
 - Callables: lambdas, functions, staticmethods, classmethods, built-in functions
 - Module types
 - IOBase
 - Iterators
 - Custom objects: instances and classes