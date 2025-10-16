from abc import ABC, abstractmethod
from dataclasses import dataclass
import random
from typing import Any, Callable, cast, get_type_hints, Optional, Protocol, TYPE_CHECKING

from pyconll.exception import ParseError

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparisonT

# TODO: What's up with "SupportsRichComparisonT"
# TODO: How to handle empty for containers appropriately and keeping same behavior as before (or better)
_used_name_ids = set[str]()

def unique_name_id(prefix: str) -> str:
    var_name = ""
    suffix = -1
    while suffix < 0 or (var_name in _used_name_ids or var_name in globals()):
        suffix = random.randint(0, 4294967296)
        var_name = f"{prefix}_{suffix}"
    _used_name_ids.add(var_name)

    return var_name

class SchemaDescriptor[T](ABC):
    @abstractmethod
    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        pass

    @abstractmethod
    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        pass

    def deserialize_codegen(self, namespace: dict[str, Any]) -> str:
        method_name = unique_name_id("deserialize_" + self.__class__.__name__)
        codegen = self.do_deserialize_codegen(namespace, method_name)
        exec(codegen, namespace)
        return method_name

    def serialize_codegen(self, namespace: dict[str, Any]) -> str:
        method_name = unique_name_id("serialize_" + self.__class__.__name__)
        codegen = self.do_serialize_codegen(namespace, method_name)
        exec(codegen, namespace)
        return method_name


@dataclass(frozen=True, slots=True)
class _NullableDescriptor[T](SchemaDescriptor[Optional[T]]):
    mapper: type[T] | SchemaDescriptor[T]
    empty_marker: Optional[str]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = ""
        if isinstance(self.mapper, SchemaDescriptor):
            sub_method_name = self.mapper.deserialize_codegen(namespace)
        elif self.mapper in (int, float):
            sub_method_name = self.mapper.__name__
        elif self.mapper != str:
            raise RuntimeError(
                "Nullable schema must map via an int, float, or str or provide a nested SchemaDescriptor."
            )

        return root_ir(f"""
            def {method_name}(val):
                if val is None:
                    return {self.empty_marker}

                return {sub_method_name}(val)
            """)

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = ""
        if isinstance(self.mapper, SchemaDescriptor):
            sub_method_name = self.mapper.serialize_codegen(namespace)
        elif self.mapper in (int, float):
            sub_method_name = self.mapper.__name__
        elif self.mapper != str:
            raise RuntimeError(
                "Nullable schema must map via an int, float, or str or provide a nested SchemaDescriptor."
            )

        return root_ir(f"""
            def {method_name}(s):
                if {self.empty_marker!r} is not None and s == {self.empty_marker!r}:
                    return None:
                return {sub_method_name}(s)
            """)


@dataclass(frozen=True, slots=True)
class _ArrayDescriptor[T](SchemaDescriptor[list[T]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    empty_marker: Optional[str]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = ""
        if isinstance(self.mapper, SchemaDescriptor):
            sub_method_name = self.mapper.deserialize_codegen(namespace)
        elif self.mapper in (int, float):
            sub_method_name = self.mapper.__name__
        elif self.mapper != str:
            raise RuntimeError(
                "Array schema must map via an int, float, or str or provide a nested SchemaDescriptor."
            )

        return root_ir(f"""
            def {method_name}(vs):
                if len(vs) == 0:
                    return "{self.empty_marker}"
                "{self.delimiter}".join({sub_method_name}(el) for el in vs)
            """)

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        result_ir = ""
        if isinstance(self.mapper, SchemaDescriptor):
            sub_method_name = self.mapper.serialize_codegen(namespace)
            result_ir = f"[{sub_method_name}(el) for el in s.split(\"{self.delimiter}\")]"
        elif self.mapper in (int, float):
            result_ir = f"[{self.mapper.__name__}(el) for el in s.split(\"{self.delimiter}\")]"
        elif self.mapper == str:
            result_ir = f"s.split(\"{self.delimiter}\")"
        else:
            raise RuntimeError(
                "Array schema must map via an int, float, or str or provide a nested SchemaDescriptor."
            )

        return root_ir(f"""
            def {method_name}(s):
                if s == {self.empty_marker!r} or len(s) == 0:
                    return []
                return {result_ir}
            """)


@dataclass(frozen=True, slots=True)
class _UniqueArrayDescriptor[T](SchemaDescriptor[set[T]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    empty_marker: Optional[str]
    ordering_key: Optional[Callable[[T], "SupportsRichComparisonT"]]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        raise NotImplementedError("You know it")

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = ""
        if isinstance(self.mapper, SchemaDescriptor):
            sub_method_name = self.mapper.serialize_codegen(namespace)
        elif self.mapper in (int, float):
            sub_method_name = self.mapper.__name__
        elif self.mapper != str:
            raise RuntimeError(
                "UniqueArray schema must wrap an int, float, or str or provide a nested SchemaDescriptor."
            )

        return root_ir(f"""
            def {method_name}(s):
                if s == {self.empty_marker!r} or not s:
                    return set()
                return {{ {sub_method_name}(el) for el in s.split("{self.delimiter}") }}
            """)


@dataclass(frozen=True, slots=True)
class _FixedArrayDescriptor[T](SchemaDescriptor[tuple[T, ...]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    min_size_req: Optional[int]
    max_size_req: Optional[int]
    empty_marker: Optional[str]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        raise NotImplementedError("You know it")

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = ""
        if isinstance(self.mapper, SchemaDescriptor):
            sub_method_name = self.mapper.serialize_codegen(namespace)
        elif self.mapper in (int, float):
            sub_method_name = self.mapper.__name__
        elif self.mapper != str:
            raise RuntimeError(
                "FixedArray schema must wrap an int, float, or str or provide a nested SchemaDescriptor."
            )

        return root_ir(f"""
            def {method_name}(s):
                if {self.empty_marker!r} is not None and s == {self.empty_marker!r}:
                    return ()
                if not s:
                    t = ()
                else:
                    t = tuple({sub_method_name}(el) for el in s.split("{self.delimiter}"))

                if {self.min_size_req} is not None and len(t) < {self.min_size_req}:
                    raise ParseError("The input \\"{{s}}\\" is parsed as a tuple smaller than the required minimum size of {self.min_size_req}")

                if {self.max_size_req} is not None and len(t) > {self.max_size_req}:
                    raise ParseError("The input \\"{{s}}\\" is parsed as a tuple smaller than the required minimum size of {self.max_size_req}")

                return t
            """)


@dataclass(frozen=True, slots=True)
class _MappingDescriptor[K, V](SchemaDescriptor[dict[K, V]]):
    kmapper: type[K] | SchemaDescriptor[K]
    vmapper: type[V] | SchemaDescriptor[V]
    pair_delimiter: str
    av_delimiter: str
    empty_marker: Optional[str]
    ordering_key: Optional[Callable[[K], "SupportsRichComparisonT"]]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        raise NotImplementedError("You know it")

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        key_sub_method_name = ""
        if isinstance(self.kmapper, SchemaDescriptor):
            key_sub_method_name = self.kmapper.serialize_codegen(namespace)
        elif self.kmapper in (int, float):
            key_sub_method_name = self.kmapper.__name__
        elif self.kmapper != str:
            raise RuntimeError(
                "Mapping key schema must wrap an int, float, or str or provide a nested SchemaDescriptor."
            )

        value_sub_method_name = ""
        if isinstance(self.vmapper, SchemaDescriptor):
            value_sub_method_name = self.vmapper.serialize_codegen(namespace)
        elif self.vmapper in (int, float):
            value_sub_method_name = self.vmapper.__name__
        elif self.vmapper != str:
            raise RuntimeError(
                "Mapping value schema must wrap an int, float, or str or provide a nested SchemaDescriptor."
            )

        return root_ir(f"""
            def {method_name}(s):
                if ({self.empty_marker!r} is not None and s == {self.empty_marker!r}) or not s:
                    return {{}}
                pairs = (el.split("{self.av_delimiter}", 1) for el in s.split("{self.pair_delimiter}"))
                return {{ {key_sub_method_name}(pair[0]): {value_sub_method_name}(pair[1]) for pair in pairs }}
            """)


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
    def conll(self) -> str: ...


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
        return attr.serialize_codegen(namespace)
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
