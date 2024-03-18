from dataclasses import dataclass
from typing import Literal

LIST_STRATEGIES = Literal["Sequence", "list"]
LIST_ELEMENT_STRATEGIES = Literal["Any", "object", "Union"]
TUPLE_STRATEGIES = Literal["Any", "object", "fix size"]
SET_STRATEGIES = Literal["Any", "object", "Union"]


@dataclass(frozen=True)
class Strategies:
    list_strategy: LIST_STRATEGIES = "list"
    list_elements_strategy: LIST_ELEMENT_STRATEGIES = "Union"
    tuple_elements_strategy: TUPLE_STRATEGIES = "fix size"
    set_elements_strategy: SET_STRATEGIES = "Union"
