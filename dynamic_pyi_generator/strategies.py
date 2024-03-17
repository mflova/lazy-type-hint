from dataclasses import dataclass

from dynamic_pyi_generator.type_aliases import (
    LIST_ELEMENT_STRATEGIES,
    LIST_STRATEGIES,
    TUPLE_STRATEGIES,
)


@dataclass(frozen=True)
class Strategies:
    list_strategy: LIST_STRATEGIES = "list"
    list_elements_strategy: LIST_ELEMENT_STRATEGIES = "Union"
    tuple_elements_strategy: TUPLE_STRATEGIES = "fix size"
