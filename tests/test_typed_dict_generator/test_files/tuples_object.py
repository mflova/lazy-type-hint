from __future__ import annotations

from typing import TypedDict
from typing import List
from typing import Set
from typing import Tuple
from typing import Union

class NewClass(TypedDict):
    name: str
    age: int
    kids: List[str]
    favourite_colors: Set[str]
    random_data: List[Union[str, int]]
    tuple_example: Tuple[object]
    address: NewClassAddress

class NewClassAddress(TypedDict):
    street: str
    city: str
    state: str