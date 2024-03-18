from dataclasses import dataclass
from typing import Literal

LIST_STRATEGIES = Literal["Sequence", "list"]
LIST_ELEMENT_STRATEGIES = Literal["Any", "object", "Union"]
TUPLE_ELEMENT_STRATEGIES = Literal["Any", "object", "Union"]
TUPLE_SIZE_STRATEGIES = Literal["fixed", "..."]
SET_STRATEGIES = Literal["Any", "object", "Union"]
MAPPING_STRATEGIES = Literal["TypedDict", "Mapping", "Dict"]


@dataclass(frozen=True)
class Strategies:
    list_strategy: LIST_STRATEGIES = "list"
    sequence_elements_strategy: LIST_ELEMENT_STRATEGIES = "Union"
    tuple_elements_strategy: TUPLE_ELEMENT_STRATEGIES = "Union"
    tuple_size_strategy: TUPLE_SIZE_STRATEGIES = "fixed"
    set_elements_strategy: SET_STRATEGIES = "Union"
    mapping_strategy: MAPPING_STRATEGIES = "TypedDict"
