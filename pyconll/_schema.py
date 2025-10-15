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
    empty_marker: Optional[str]


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
    min_size_req: Optional[int]
    max_size_req: Optional[int]
    empty_marker: Optional[str]


@dataclass(frozen=True, slots=True)
class _MappingDescriptor[K, V](SchemaDescriptor[dict[K, V]]):
    kmapper: type[K] | SchemaDescriptor[K]
    vmapper: type[V] | SchemaDescriptor[V]
    pair_delimiter: str
    av_delimiter: str
    empty_marker: Optional[str]
    ordering_key: Optional[Callable[[K], "SupportsRichComparisonT"]]


def nullable[T](mapper: type[T] | SchemaDescriptor[T], empty_marker: Optional[str] = None) -> _NullableDescriptor[T]:
    return _NullableDescriptor[T](mapper, empty_marker)


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
    min_size_req: Optional[int] = None,
    max_size_req: Optional[int] = None,
    empty_marker: Optional[str] = None,
) -> _FixedArrayDescriptor[T]:
    return _FixedArrayDescriptor[T](mapper, delimiter, min_size_req, max_size_req, empty_marker)


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


class ConlluToken(TokenProtocol):
    id: str
    form: Optional[str] = schema(nullable(str, "_"))
    lemma: Optional[str] = schema(nullable(str, "_"))
    upos: Optional[str] = schema(nullable(str, "_"))
    xpos: Optional[str] = schema(nullable(str, "_"))
    feats: dict[str, set[str]] = schema(mapping(str, unique_array(str, ","), "|", "=", "_", lambda k: k.lower()))
    head: Optional[str] = schema(nullable(str, "_"))
    deprel: Optional[str] = schema(nullable(str, "_"))
    deps: dict[str, tuple[str, ...]] = schema(mapping(str, fixed_array(str, ':', None, 4), "|", ":", "_"))
    misc: dict[str, Optional[set[str]]] = schema(mapping(str, nullable(unique_array(str, ",")), "|", "=", "_", lambda k: k.lower()))

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

def root_ir(code: str) -> str:
    lines = code.split("\n")
    if not lines:
        return code

    for first, line in enumerate(lines):
        if line:
            break
    else:
        return code

    prefix_chars = []
    for ch in lines[first]:
        if ch not in ' \t':
            break
        if ch != lines[first][0]:
            raise RuntimeError("Inconsistent whitespace usage in IR being reformatted.")

        prefix_chars.append(ch)
    prefix = "".join(prefix_chars)

    new_lines = [lines[first].removeprefix(prefix)]
    for line in lines[first + 1:]:
        if not line:
            continue
        if not line.startswith(prefix):
            raise RuntimeError("Expected whitespace prefix not found on one of the IR lines.")

        new_lines.append(line.removeprefix(prefix))

    return "\n".join(new_lines)


def splice_ir(levels: int, code: str) -> str:
    prefix = ' ' * 4 * levels
    return "\n".join([prefix + line if i > 0 else line for i, line in enumerate(code.split("\n"))])


def add_schema_descriptor_method(namespace: dict[str, Any], descriptor: SchemaDescriptor) -> str:
    method_name = unique_name_id("mfd_" + descriptor.__class__.__name__)

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

        guard_ir = ""
        if descriptor.empty_marker is not None:
            guard_ir = root_ir(f"""
                if s == "{descriptor.empty_marker}":
                    return None
                """)

        method_ir = root_ir(f"""
            def {method_name}(s):
                if not s:
                    return None
                {splice_ir(4, guard_ir)}
                else:
                    return {sub_method_name}(s)
            """)

    elif isinstance(descriptor, _ArrayDescriptor):
        result_ir = ""
        mapper = descriptor.mapper
        if isinstance(mapper, SchemaDescriptor):
            sub_method_name = add_schema_descriptor_method(namespace, mapper)
            result_ir = f"[{sub_method_name}(el) for el in s.split(\"{descriptor.delimiter}\")]"
        elif mapper in (int, float):
            result_ir = f"[{mapper.__name__}(el) for el in s.split(\"{descriptor.delimiter}\")]"
        elif mapper == str:
            result_ir = f"s.split(\"{descriptor.delimiter}\")"
        else:
            raise RuntimeError(
                "Nullable schema must map via an int, float, or str or provide a nested SchemaDescriptor."
            )

        guard_ir = ""
        if descriptor.empty_marker is not None:
            guard_ir = root_ir(f"""
                if s == "{descriptor.empty_marker}":
                    return []
                """)

        method_ir = root_ir(f"""
            def {method_name}(s):
                {splice_ir(4, guard_ir)}
                if not s:
                    return []
                return {result_ir}
            """)

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

        guard_ir = ""
        if descriptor.empty_marker is not None:
            guard_ir = root_ir(f"""
                if s == "{descriptor.empty_marker}":
                    return set()
                """)

        method_ir = root_ir(f"""
            def {method_name}(s):
                {splice_ir(4, guard_ir)}
                if not s:
                    return set()
                return {{ {sub_method_name}(el) for el in s.split("{descriptor.delimiter}") }}
            """)

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

        empty_guard_ir = ""
        if descriptor.empty_marker is not None:
            empty_guard_ir = root_ir(f"""
                if s == "{descriptor.empty_marker}":
                    return ()
                """)

        guard_ir = ""
        if descriptor.min_size_req is not None:
            guard_ir += root_ir(f"""
                if len(t) < {descriptor.min_size_req}:
                    raise ParseError("The input \\"{{s}}\\" is parsed as a tuple smaller than the required minimum size of {descriptor.min_size_req}")
                """)
        if descriptor.max_size_req is not None:
            guard_ir += root_ir(f"""
                if len(t) > {descriptor.max_size_req}:
                    raise ParseError("The input \\"{{s}}\\" is parsed as a tuple smaller than the required minimum size of {descriptor.max_size_req}")
                """)

        method_ir = root_ir(f"""
            def {method_name}(s):
                {splice_ir(4, empty_guard_ir)}
                if not s:
                    t = ()
                else:
                    t = tuple({sub_method_name}(el) for el in s.split("{descriptor.delimiter}"))
                {splice_ir(4, guard_ir)}
                return t
            """)

    elif isinstance(descriptor, _MappingDescriptor):
        key_sub_method_name = ""
        kmapper = descriptor.kmapper
        if isinstance(kmapper, SchemaDescriptor):
            key_sub_method_name = add_schema_descriptor_method(namespace, kmapper)
        elif kmapper in (int, float):
            key_sub_method_name = kmapper.__name__
        elif kmapper != str:
            raise RuntimeError(
                "Mapping key schema must wrap an int, float, or str or provide a nested SchemaDescriptor."
            )

        value_sub_method_name = ""
        vmapper = descriptor.vmapper
        if isinstance(vmapper, SchemaDescriptor):
            value_sub_method_name = add_schema_descriptor_method(namespace, vmapper)
        elif vmapper in (int, float):
            value_sub_method_name = vmapper.__name__
        elif vmapper != str:
            raise RuntimeError(
                "Mapping value schema must wrap an int, float, or str or provide a nested SchemaDescriptor."
            )

        guard_ir = ""
        if descriptor.empty_marker is not None:
            guard_ir = root_ir(f"""
                if s == "{descriptor.empty_marker}":
                    return {{}}
                """)

        method_ir = root_ir(f"""
            def {method_name}(s):
                {splice_ir(4, guard_ir)}
                if not s:
                    return {{}}
                pairs = (el.split("{descriptor.av_delimiter}", 1) for el in s.split("{descriptor.pair_delimiter}"))
                return {{ {key_sub_method_name}(pair[0]): {value_sub_method_name}(pair[1]) for pair in pairs }}
            """)

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

    unique_token_name = unique_name_id("Token")
    class_ir = root_ir(f"""
        class {unique_token_name}({s.__name__}):
            __slots__ = (\"{"\", \"".join(field_names)}\",)

            def __init__(self, {", ".join(field_names)}) -> None:
                {"\n                ".join(f"self.{fn} = {fn}" for fn in field_names)}
        """)
    exec(class_ir, namespace)

    compiled_parse_token = unique_name_id("compiled_parse_token")
    compiled_parse_token_ir = root_ir(f"""
        def {compiled_parse_token}(line: str) -> {s.__name__}:
            fields = line.split("\\t")

            if len(fields) != {len(field_names)}:
                error_msg = f"The number of columns per token line must be {len(field_names)}. Invalid token: {{line!r}}"
                raise ParseError(error_msg)

            if len(fields[-1]) > 0 and fields[-1][-1] == "\\n":
                fields[-1] = fields[-1][:-1]

            {"\n            ".join(field_irs)}

            return {unique_token_name}({",".join(field_names)})
        """)

    exec(compiled_parse_token_ir, namespace)
    parser = cast(Callable[[str], S], namespace[compiled_parse_token])
    return parser
