# TODO

feat:

- Create `TypedDict` with docstrings if those are present within a file
- Check behaviour with a dict with multiple lists (equal and different ones)
- Generating `.py` files locally:
  - Allow different subfolders
  - Think from a collaborative point of view: Think that the `.pyi` file will not be up
    to date. Therefore I cannot use it to check the existing `.py` files
  - Ideas:
    - Have a file in the root of the repo that will keep track of all custom classes created.
    - Detect that these are generated custom classes by looking at the header "Do not modify"

refactor:

- Rename main class
- Make it easier to import for users

docs:

- Edit README.md:
  - Explain some differences like: "Cattrs or pydantic require knowing the structure you
    want to cast beforehand. They are validation-oriented. Although my tool can be used
    for validation, it is more geared towards providing better type hints and ensuring
    that the structure is accessed correctly. Stubgen generates the pyi file for you, but
    then you have to work with files until you can use it. It's not always easy to
    organize.
- Better docstrings (specially for parsers)

ci:

- Setup pipelines
- Setup branch protection

tests:
- test main API features:
    - Add flag "if intefcace exists = Literal["validate", "overwrite"]"
