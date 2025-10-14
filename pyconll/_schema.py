from dataclasses import dataclass, field
import random
from typing import Any, Callable, cast, get_type_hints, Optional, Protocol, TYPE_CHECKING

from pyconll.exception import ParseError

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparisonT

# TODO: What's up with "SupportsRichComparisonT"
# TODO: How to handle empty for containers appropriately and keeping same behavior as before (or better)


class SchemaDescriptor[T]:
    pass


@dataclass(frozen=True, slots=True)
class _NullableDescriptor[T](SchemaDescriptor[Optional[T]]):
    mapper: type[T] | SchemaDescriptor[T]
    empty: str


@dataclass(frozen=True, slots=True)
class _ArrayDescriptor[T](SchemaDescriptor[list[T]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    empty_marker: Optional[str]


@dataclass(frozen=True, slots=True)
class _UniqueArrayDescriptor[T](SchemaDescriptor[set[T]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    empty_marker: Optional[str]
    ordering_key: Optional[Callable[[T], "SupportsRichComparisonT"]]


@dataclass(frozen=True, slots=True)
class _FixedArrayDescriptor[T](SchemaDescriptor[tuple[T, ...]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    length: int
    empty_marker: Optional[str]


@dataclass(frozen=True, slots=True)
class _MappingDescriptor[K, V](SchemaDescriptor[dict[K, V]]):
    kmapper: type[K] | SchemaDescriptor[K]
    vmapper: type[V] | SchemaDescriptor[V]
    pair_delimiter: str
    av_delimiter: str
    empty_marker: Optional[str]
    ordering_key: Optional[Callable[[K], "SupportsRichComparisonT"]]


def nullable[T](mapper: type[T] | SchemaDescriptor[T], empty: str) -> _NullableDescriptor[T]:
    return _NullableDescriptor[T](mapper, empty)


def array[T](
    mapper: type[T] | SchemaDescriptor[T], delimiter: str, empty_marker: Optional[str] = None
) -> _ArrayDescriptor[T]:
    return _ArrayDescriptor[T](mapper, delimiter, empty_marker)


def unique_array[T](
    el_mapper: type[T] | SchemaDescriptor[T],
    delimiter: str,
    empty_marker: Optional[str] = None,
    ordering_key: Optional[Callable[[T], Any]] = None,
) -> _UniqueArrayDescriptor[T]:
    return _UniqueArrayDescriptor(el_mapper, delimiter, empty_marker, ordering_key)


def fixed_array[T](
    mapper: type[T] | SchemaDescriptor[T],
    delimiter: str,
    length: int,
    empty_marker: Optional[str] = None,
) -> _FixedArrayDescriptor[T]:
    return _FixedArrayDescriptor[T](mapper, delimiter, length, empty_marker)


def mapping[K, V](
    kmapper: type[K] | SchemaDescriptor[K],
    vmapper: type[V] | SchemaDescriptor[V],
    pair_delimiter: str,
    av_delimiter: str,
    empty_marker: Optional[str] = None,
    ordering_key: Optional[Callable[[K], Any]] = None,
) -> _MappingDescriptor[K, V]:
    return _MappingDescriptor[K, V](
        kmapper, vmapper, pair_delimiter, av_delimiter, empty_marker, ordering_key
    )


def schema[T](desc: SchemaDescriptor[T]) -> T:
    return cast(T, desc)


class TokenProtocol(Protocol):
    pass


a = schema(mapping(str, array(int, ","), ";", "=", "_"))


class ConlluToken(TokenProtocol):
    id: str
    # form: Optional[str] = schema(nullable("_", str))
    # lemma: Optional[str] = optional[str]("_")
    # upos: Optional[str] = optional[str]("_")
    # xpos: Optional[str] = optional[str]("_")
    # feats: dict[str, set[str]] = mapping[str, set[str]](
    #    "_", "|", "=", vmapper=array_set(","), ordering_key=lambda k: k.lower()
    # )
    # head: Optional[str] = optional[str]("_")
    # deprel: Optional[str] = optional[str]("_")
    # deps: dict[str, tuple[str, str, str, str]] = mapping[str, tuple[str, str, str, str]](
    #    "_", "|", ":", vmapper=array_tuple[str, str, str, str](":")
    # )
    # misc: dict[str, Optional[set[str]]] = mapping[str, Optional[set[str]]](
    #    "_",
    #    "|",
    #    "=",
    #    vmapper=optional("_", mapper=array_set[str](",")),
    #    ordering_key=lambda k: k.lower(),
    # )

    def is_multiword(self) -> bool:
        """
        Checks if this Token is a multiword token.

        Returns:
            True if this token is a multiword token, and False otherwise.
        """
        return "-" in self.id

    def is_empty_node(self) -> bool:
        """
        Checks if this Token is an empty node, used for ellipsis annotation.

        Note that this is separate from any field being empty, rather it means
        the id has a period in it.

        Returns:
            True if this token is an empty node and False otherwise.
        """
        return "." in self.id


_used_name_ids = set[str]()


def unique_name_id(prefix: str) -> str:
    var_name = ""
    suffix = -1
    while suffix < 0 or (var_name in _used_name_ids or var_name in globals()):
        suffix = random.randint(0, 4294967296)
        var_name = f"{prefix}_{suffix}"
    _used_name_ids.add(var_name)

    return var_name


def add_schema_descriptor_method(namespace: dict[str, Any], descriptor: SchemaDescriptor) -> str:
    method_name = unique_name_id("mfd")

    if isinstance(descriptor, _NullableDescriptor):
        sub_method_name = ""
        mapper = descriptor.mapper
        if isinstance(mapper, SchemaDescriptor):
            sub_method_name = add_schema_descriptor_method(namespace, mapper)
        elif mapper in (int, float):
            sub_method_name = mapper.__name__
        elif mapper != str:
            raise RuntimeError(
                "Nullable schema must map via an int, float, or str or provide a nested SchemaDescriptor."
            )

        method_ir = f"""
def {method_name}(s):
    if s == "{descriptor.empty}":
        return None
    else:
        return {sub_method_name}(s)
"""

    elif isinstance(descriptor, _MappingDescriptor):
        pass
    elif isinstance(descriptor, _UniqueArrayDescriptor):
        sub_method_name = ""
        mapper = descriptor.mapper
        if isinstance(mapper, SchemaDescriptor):
            sub_method_name = add_schema_descriptor_method(namespace, mapper)
        elif mapper in (int, float):
            sub_method_name = mapper.__name__
        elif mapper != str:
            raise RuntimeError(
                "UniqueArray schema must wrap an int, float, or str or provide a nested SchemaDescriptor."
            )

        method_ir = f"""
def {method_name}(s):
    return {{ {sub_method_name}(el) for el in s.split("{descriptor.delimiter}") }}
"""
    elif isinstance(descriptor, _FixedArrayDescriptor):
        sub_method_name = ""
        mapper = descriptor.mapper
        if isinstance(mapper, SchemaDescriptor):
            sub_method_name = add_schema_descriptor_method(namespace, mapper)
        elif mapper in (int, float):
            sub_method_name = mapper.__name__
        elif mapper != str:
            raise RuntimeError(
                "FixedArray schema must wrap an int, float, or str or provide a nested SchemaDescriptor."
            )

        method_ir = f"""
def {method_name}(s):
    t = tuple({sub_method_name}(el) for el in s.split("{descriptor.delimiter}"))
    if len(t) != {descriptor.length}:
        raise RuntimeError("The length of the FixedArray is not the expected length.")
    return t
"""
    else:
        raise RuntimeError("The SchemaDescriptor could not be transformed into IR.")

    exec(method_ir, namespace)
    return method_name


def compile_schema_ir(
    namespace: dict[str, Any], attr: Optional[SchemaDescriptor], type_hint: type
) -> str:
    if attr is None:
        # If there is no value on the protocol's attribute then the type hint is used directly. In this case,
        # only str, int, and float should really be handled, since all other types, will have more ambiguous
        # (de)serialization semantics that needs to be explicitly defined.
        if type_hint == str:
            return ""
        elif type_hint == int:
            return "int"
        elif type_hint == float:
            return "float"
        else:
            raise RuntimeError(
                "Only str, int, and float are directly supported for column schemas. For other types, define the schema via SchemaDescriptors."
            )
    elif isinstance(attr, SchemaDescriptor):
        method_name = add_schema_descriptor_method(namespace, attr)
        return method_name
    else:
        raise RuntimeError(
            "Attributes for column schemas must either be unassigned (None) or a SchemaDescriptor."
        )


def compile_token_parser[S: TokenProtocol](s: type[S]) -> Callable[[str], S]:
    hints = get_type_hints(s)

    field_names = []
    field_irs: list[str] = []
    namespace = {
        s.__name__: s,
        "ParseError": ParseError,
    }

    for i, (name, type_hint) in enumerate(hints.items()):
        attr = getattr(s, name) if hasattr(s, name) else None
        method_name = compile_schema_ir(namespace, attr, type_hint)
        field_ir = f"{name} = {method_name}(fields[{i}])"

        field_names.append(name)
        field_irs.append(field_ir)

    # TODO: Create ability to simplify ir, based on first line, identation.
    unique_token_name = unique_name_id("Token")
    class_ir = f"""
class {unique_token_name}({s.__name__}):
    __slots__ = (\"{"\", \"".join(field_names)}\",)

    def __init__(self, {", ".join(field_names)}) -> None:
        {"\n        ".join(f"self.{fn} = {fn}" for fn in field_names)}
"""
    exec(class_ir, namespace)

    compiled_parse_token = unique_name_id("compiled_parse_token")
    compiled_parse_token_ir = f"""
def {compiled_parse_token}(line: str) -> {s.__name__}:
    fields = line.split("\\t")

    if len(fields) != {len(field_names)}:
        error_msg = f"The number of columns per token line must be {len(field_names)}. Invalid token: {{line!r}}"
        raise ParseError(error_msg)

    if fields[-1][-1] == "\\n":
        fields[-1] = fields[-1][:-1]

    {"\n    ".join(field_irs)}

    return {unique_token_name}({",".join(field_names)})
"""

    exec(compiled_parse_token_ir, namespace)
    parser = cast(Callable[[str], S], namespace[compiled_parse_token])
    return parser
