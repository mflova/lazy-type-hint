from dataclasses import dataclass, fields
from typing import Literal, Optional, get_args, get_type_hints

LIST_STRATEGIES = Literal["Sequence", "list"]
TUPLE_SIZE_STRATEGIES = Literal["fixed", "any size"]
MAPPING_STRATEGIES = Literal["TypedDict", "Mapping", "dict"]
PANDAS_STRATEGIES = Literal["Full type hint", "Type hint only for autocomplete", "Do not type hint columns"]


@dataclass(frozen=True)
class ParsingStrategies:
    list_strategy: LIST_STRATEGIES = "list"
    tuple_size_strategy: TUPLE_SIZE_STRATEGIES = "fixed"
    dict_strategy: MAPPING_STRATEGIES = "TypedDict"
    pandas_strategies: PANDAS_STRATEGIES = "Full type hint"
    min_height_to_define_type_alias: int = 1
    key_used_as_doc: str = ""
    merge_different_typed_dicts_if_similarity_above: int = 50
    typed_dict_read_only_values: bool = False
    check_max_n_elements_within_container: Optional[int] = 500

    def __post_init__(self) -> None:
        type_hints = get_type_hints(self)
        for field in fields(type(self)):
            allowed_values = get_args(type_hints[field.name])
            if (
                allowed_values
                and all(isinstance(value, str) for value in allowed_values)
                and getattr(self, field.name) not in allowed_values
            ):
                raise ValueError(
                    f"Invalid value for {field.name}. Expected any of ({', '.join(map(str, allowed_values))}) but got "
                    f"{getattr(self, field.name)}"
                )
        if self.min_height_to_define_type_alias < 0:
            raise ValueError("`min_height_to_define_type_alias` must be greater or equal than 0")

        if self.merge_different_typed_dicts_if_similarity_above <= 0:
            raise ValueError("`merge_typed_dicts_if_similarity_above` must be greater than 0")
        if self.merge_different_typed_dicts_if_similarity_above > 100:
            raise ValueError("`merge_typed_dicts_if_similarity_above` must be less than 100")
        if self.check_max_n_elements_within_container and self.check_max_n_elements_within_container <= 0:
            raise ValueError("`chec_max_n_type_elements_within_container` must at least 1")