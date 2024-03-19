from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    ClassVar,
    Dict,
    Final,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    final,
)

from dynamic_pyi_generator.strategies import Strategies


class ParserError(Exception):
    ...


@dataclass
class ParseOutput:
    string_representation: str
    imports: Set[str] = field(default_factory=set)
    to_process: List[Tuple[str, object]] = field(default_factory=list)


DataT_contra = TypeVar("DataT_contra", contravariant=True)


class Parser(Generic[DataT_contra]):
    imports: Set[str]
    parsers: ClassVar[Dict[Type[object], Parser[Any]]] = {}
    this_one_parses: ClassVar[Union[Type[object], Tuple[Type[object], ...]]] = object
    to_process: list[Tuple[str, object]]
    strategies: Strategies

    # Constants
    suffix_repeated_classes: Final = "_{idx}"

    def __init__(self, strategies: Optional[Strategies] = None):
        self.to_process = []
        self.imports = set()
        if not strategies:
            self.strategies = Strategies()
        else:
            self.strategies = strategies

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if cls.this_one_parses == object:
            raise ParserError(
                "`this_one_parses` must be overriden for each `Parser` subclass."
            )
        if isinstance(cls.this_one_parses, Iterable):
            for element in cls.this_one_parses:
                cls.parsers[element] = cls  # type: ignore
        else:
            cls.parsers[cls.this_one_parses] = cls  # type: ignore

    @final
    def parse(self, data: DataT_contra, *, class_name: str) -> str:
        outputs_collected: List[ParseOutput] = []

        # Instantiate a single parser for the main data type
        parser = self.create_parser(data, strategies=self.strategies)
        outputs_collected.append(
            parser._parse(data, class_name=class_name)  # noqa: SLF001
        )

        # Process in loop all the requested subclasses found within the inner structure
        # of the main class
        to_process: List[Tuple[str, object]] = outputs_collected[0].to_process
        while to_process:
            name, object_ = to_process.pop()
            parser = self.create_parser(object_, strategies=self.strategies)
            outputs_collected.append(parser._parse(object_, class_name=name))  # type: ignore  # noqa: SLF001
            to_process.extend(outputs_collected[-1].to_process)
        return self.format_file(outputs_collected)

    @final
    def format_file(self, outputs_collected: Sequence[ParseOutput]) -> str:
        imports: Set[str] = set()
        for output in outputs_collected:
            imports.update(output.imports)
        string = "\n".join(sorted(imports))
        string += "\n\n"
        string += "\n\n".join(
            output.string_representation for output in outputs_collected[::-1]
        )
        return string

    @staticmethod
    def create_parser(
        data: object, *, strategies: Optional[Strategies] = None
    ) -> Parser[DataT_contra]:
        try:
            return Parser.parsers[type(data)](strategies=strategies)  # type: ignore
        except KeyError as error:
            raise ParserError(
                f"There is no parser for the given data type: {type(data).__name__}"
            ) from error

    def _parse(self, data: DataT_contra, *, class_name: str) -> ParseOutput:
        raise NotImplementedError

    def process_elements(
        self, data: Iterable[Any], *, class_name: str, include_repeated: bool = False
    ) -> List[str]:
        subtypes: Union[List[str], Set[str]] = [] if include_repeated else set()

        def add_subtype(value: str) -> None:
            if include_repeated:
                subtypes.append(value)  # type: ignore
            else:
                subtypes.add(value)  # type: ignore

        for element_class_name, object_ in self._get_elements_info(
            data, current_class_name=class_name
        ).items():
            if type(object_) not in self.simple_types:
                add_subtype(element_class_name)
                self.to_process.append((element_class_name, object_))
                new_class_name = element_class_name
            else:
                new_class_name = type(object_).__name__
            add_subtype(new_class_name)

        if "float" in subtypes and "int" in subtypes and not include_repeated:
            subtypes.remove("int")
        return sorted(subtypes)

    def _build_union_elements(self, elements: Union[Set[str], Sequence[str]]) -> str:
        if len(elements) == 1:
            return next(iter(elements))
        else:
            self.imports.add("from typing import Union")
            return f"Union[{', '.join(elements)}]"

    def _get_elements_info(
        self, data: Iterable[Any], *, current_class_name: str
    ) -> Mapping[str, object]:
        # key: new hypotehtic name.
        # value: object itself

        dct: Dict[str, object] = {}
        for element in data:
            name = f"{current_class_name}{type(element).__name__.capitalize()}"
            modified_name = name
            count = 0
            while modified_name in dct:
                modified_name = name + self.suffix_repeated_classes.format(idx=count)
                count += 1
            dct[modified_name] = element
        return dct

    @final
    @property
    def simple_types(self) -> Set[Type[object]]:
        return {str, int, float}

    @staticmethod
    def to_camel_case(string: str) -> str:
        words = string.split("_")
        return words[0].capitalize() + "".join(
            palabra.capitalize() for palabra in words[1:]
        )
