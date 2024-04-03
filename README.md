# dynamic_pyi_generator
Work in progress tool that generates corresponding .pyi files in the fly from JSON, YAML...

## Features

Main features:
 - Type hint any (nested) structure.
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
 - Simple built-in types: bool, int, float, range, slice, None, str
 - Callables: lambdas, functions, staticmethods, classmethods
 - Custom objects: instances and classes