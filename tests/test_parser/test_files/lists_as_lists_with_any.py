from typing import Any
from typing import List
from typing import Set
from typing import Tuple
from typing import TypedDict

NewClassKids = List[Any]
NewClassFavouriteColors = Set[str]
NewClassRandomData = List[Any]
NewClassTupleExample = Tuple[int, str]
class NewClassAddress(TypedDict):
    street: str
    city: str
    state: str

class NewClass(TypedDict):
    name: str
    age: int
    kids: NewClassKids
    favourite_colors: NewClassFavouriteColors
    random_data: NewClassRandomData
    tuple_example: NewClassTupleExample
    address: NewClassAddress
