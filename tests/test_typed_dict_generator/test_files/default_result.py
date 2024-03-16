from __future__ import annotations

from typing import TypedDict
from typing import Union
from typing import Sequence
from typing import Set

class NewClass(TypedDict):
    name: str
    age: int
    kids: Sequence[str]
    favourite_colors: Set[str]
    random_data: Sequence[Union[str, int]]
    address: NewClassAddress

class NewClassAddress(TypedDict):
    street: str
    city: str
    state: str