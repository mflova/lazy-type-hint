from typing import TYPE_CHECKING, Literal

LIST_STRATEGIES = Literal["Sequence", "list"]
LIST_ELEMENT_STRATEGIES = Literal["Any", "object", "Union"]
TUPLE_STRATEGIES = Literal["Any", "object", "fix size"]
