from __future__ import annotations

from typing import TypedDict
from typing import List
from typing import Set
from typing import Tuple

class NewClass(TypedDict):
    name: str
    age: int
    kids: List[object]
    favourite_colors: Set[str]
    random_data: List[object]
    tuple_example: Tuple[int, str]
    address: NewClassAddress

class NewClassAddress(TypedDict):
    street: str
    city: str
    state: str