from typing import Any
from typing import List
from typing import Set
from typing import Tuple
from typing import TypedDict
from typing import Union

NewClassNumbers = List[float]

NewClassNumbersTuple = Tuple[Any, Any]

NewClassKids = List[str]

NewClassRandomDict = TypedDict(
    "NewClassRandomDict",
    {
        "1$": int,
        "2 3": float,
    },
)

NewClassFavouriteColors = Set[str]

NewClassRandomData = List[Union[int, str]]

NewClassTupleExample = Tuple[Any, Any]

class NewClassAddress(TypedDict):
    street: str
    city: str
    state: str

class NewClass(TypedDict):
    name: str
    age: int
    numbers: NewClassNumbers
    numbers_tuple: NewClassNumbersTuple
    kids: NewClassKids
    random_dict: NewClassRandomDict
    favourite_colors: NewClassFavouriteColors
    random_data: NewClassRandomData
    tuple_example: NewClassTupleExample
    address: NewClassAddress