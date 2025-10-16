from abc import ABC, abstractmethod
from dataclasses import dataclass
import random
from typing import (
    Any,
    Callable,
    cast,
    get_type_hints,
    Optional,
    Protocol,
    runtime_checkable,
    TYPE_CHECKING,
)

from pyconll.exception import ParseError
from pyconll.conllable import Conllable

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparisonT

# TODO: Figure out how to consistenly handle empty fields
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


def deserialize_sub_method_name[T](
    namespace: dict[str, Any], mapper: type[T] | SchemaDescriptor[T]
) -> str:
    if isinstance(mapper, SchemaDescriptor):
        return mapper.deserialize_codegen(namespace)

    if mapper in (int, float):
        return mapper.__name__

    if mapper == str:
        return ""

    raise RuntimeError("Mapper must map via an int, float, or str or a nested SchemaDescriptor.")


def serialize_sub_method_name[T](
    namespace: dict[str, Any], mapper: type[T] | SchemaDescriptor[T]
) -> str:
    if isinstance(mapper, SchemaDescriptor):
        return mapper.serialize_codegen(namespace)

    if mapper in (int, float):
        return "str"

    if mapper == str:
        return ""

    raise RuntimeError("Mapper must map via an int, float, or str or a nested SchemaDescriptor.")


@dataclass(frozen=True, slots=True)
class _NullableDescriptor[T](SchemaDescriptor[Optional[T]]):
    mapper: type[T] | SchemaDescriptor[T]
    empty_marker: Optional[str]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = deserialize_sub_method_name(namespace, self.mapper)
        return root_ir(
            f"""
            def {method_name}(s):
                if {self.empty_marker!r} != None and s == {self.empty_marker!r}:
                    return None
                return {sub_method_name}(s)
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = serialize_sub_method_name(namespace, self.mapper)
        return root_ir(
            f"""
            def {method_name}(val):
                if val is None:
                    return {self.empty_marker!r}

                return {sub_method_name}(val)
            """
        )


@dataclass(frozen=True, slots=True)
class _ArrayDescriptor[T](SchemaDescriptor[list[T]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    empty_marker: Optional[str]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = deserialize_sub_method_name(namespace, self.mapper)
        if sub_method_name == "":
            result_ir = f's.split("{self.delimiter}")'
        else:
            result_ir = f'[{sub_method_name}(el) for el in s.split("{self.delimiter}")]'

        return root_ir(
            f"""
            def {method_name}(s):
                if s == {self.empty_marker!r} or len(s) == 0:
                    return []
                return {result_ir}
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = serialize_sub_method_name(namespace, self.mapper)

        return root_ir(
            f"""
            def {method_name}(vs):
                if len(vs) == 0:
                    return "{self.empty_marker}"
                "{self.delimiter}".join({sub_method_name}(el) for el in vs)
            """
        )


@dataclass(frozen=True, slots=True)
class _UniqueArrayDescriptor[T](SchemaDescriptor[set[T]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    empty_marker: Optional[str]
    ordering_key: Optional[Callable[[T], "SupportsRichComparisonT"]]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = deserialize_sub_method_name(namespace, self.mapper)
        return root_ir(
            f"""
            def {method_name}(s):
                if {self.empty_marker!r} != None and s == {self.empty_marker!r} or not s:
                    return set()
                return {{ {sub_method_name}(el) for el in s.split({self.delimiter!r}) }}
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = serialize_sub_method_name(namespace, self.mapper)

        if self.ordering_key is not None:
            ordering_key_id = unique_name_id("_UniqueArrayDescriptor_ordering_key")
            namespace[ordering_key_id] = self.ordering_key
            values_ir = f"sorted(vs, key={ordering_key_id})"
        else:
            values_ir = "vs"

        return root_ir(
            f"""
            def {method_name}(vs):
                if {self.empty_marker!r} != None and len(vs) == 0:
                    return {self.empty_marker!r}
                
                return {self.delimiter!r}.join({sub_method_name}(el) for el in {values_ir})
            """
        )


@dataclass(frozen=True, slots=True)
class _FixedArrayDescriptor[T](SchemaDescriptor[tuple[T, ...]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    empty_marker: Optional[str]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = deserialize_sub_method_name(namespace, self.mapper)
        return root_ir(
            f"""
            def {method_name}(s):
                if ({self.empty_marker!r} != None and s == {self.empty_marker!r}) or (not s):
                    return ()

                return tuple({sub_method_name}(el) for el in s.split("{self.delimiter}"))
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = serialize_sub_method_name(namespace, self.mapper)
        return root_ir(
            f"""
            def {method_name}(tup):
                if {self.empty_marker!r} != None and len(tup) == 0:
                    return {self.empty_marker!r}

                return {self.delimiter!r}.join({sub_method_name}(el) for el in tup)
            """
        )


@dataclass(frozen=True, slots=True)
class _MappingDescriptor[K, V](SchemaDescriptor[dict[K, V]]):
    kmapper: type[K] | SchemaDescriptor[K]
    vmapper: type[V] | SchemaDescriptor[V]
    pair_delimiter: str
    av_delimiter: str
    empty_marker: Optional[str]
    ordering_key: Optional[Callable[[tuple[K, V]], "SupportsRichComparisonT"]]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        key_sub_method_name = deserialize_sub_method_name(namespace, self.kmapper)
        value_sub_method_name = deserialize_sub_method_name(namespace, self.vmapper)
        return root_ir(
            f"""
            def {method_name}(s):
                if ({self.empty_marker!r} != None and s == {self.empty_marker!r}) or not s:
                    return {{}}
                pairs = (el.split("{self.av_delimiter}", 1) for el in s.split("{self.pair_delimiter}"))
                return {{ {key_sub_method_name}(pair[0]): {value_sub_method_name}(pair[1]) for pair in pairs }}
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        key_sub_method_name = serialize_sub_method_name(namespace, self.kmapper)
        value_sub_method_name = serialize_sub_method_name(namespace, self.vmapper)

        if self.ordering_key is not None:
            ordering_key_id = unique_name_id("_MappingDescriptor_ordering_key")
            namespace[ordering_key_id] = self.ordering_key
            items_ir = f"items = sorted(mapping.items(), key={ordering_key_id})"
        else:
            items_ir = "items = sorted(mapping.items())"

        return root_ir(
            f"""
            def {method_name}(mapping):
                if {self.empty_marker!r} != None and len(mapping) == 0:
                    return {self.empty_marker!r}

                {items_ir}
                transformed = ({self.av_delimiter!r}.join(({key_sub_method_name}(key), {value_sub_method_name}(value))) for (key, value) in items)
                return {self.pair_delimiter!r}.join(transformed)
            """
        )


def nullable[T](
    mapper: type[T] | SchemaDescriptor[T], empty_marker: Optional[str] = None
) -> _NullableDescriptor[T]:
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
    empty_marker: Optional[str] = None,
) -> _FixedArrayDescriptor[T]:
    return _FixedArrayDescriptor[T](mapper, delimiter, empty_marker)


def mapping[K, V](
    kmapper: type[K] | SchemaDescriptor[K],
    vmapper: type[V] | SchemaDescriptor[V],
    pair_delimiter: str,
    av_delimiter: str,
    empty_marker: Optional[str] = None,
    ordering_key: Optional[Callable[[tuple[K, V]], Any]] = None,
) -> _MappingDescriptor[K, V]:
    return _MappingDescriptor[K, V](
        kmapper, vmapper, pair_delimiter, av_delimiter, empty_marker, ordering_key
    )


def schema[T](desc: SchemaDescriptor[T]) -> T:
    return cast(T, desc)


class TokenProtocol(Conllable, Protocol):
    pass


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
        if ch not in " \t":
            break
        if ch != lines[first][0]:
            raise RuntimeError("Inconsistent whitespace usage in IR being reformatted.")

        prefix_chars.append(ch)
    prefix = "".join(prefix_chars)

    new_lines = [lines[first].removeprefix(prefix)]
    for line in lines[first + 1 :]:
        if not line:
            continue
        if not line.startswith(prefix):
            raise RuntimeError("Expected whitespace prefix not found on one of the IR lines.")

        new_lines.append(line.removeprefix(prefix))

    return "\n".join(new_lines)


def splice_ir(levels: int, code: str) -> str:
    prefix = " " * 4 * levels
    return "\n".join([prefix + line if i > 0 else line for i, line in enumerate(code.split("\n"))])


def compile_deserialize_schema_ir(
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
        return attr.deserialize_codegen(namespace)

    raise RuntimeError(
        "Attributes for column schemas must either be unassigned (None) or a SchemaDescriptor."
    )


def compile_serialize_schema_ir(
    namespace: dict[str, Any], attr: Optional[SchemaDescriptor], type_hint: type
) -> str:
    if attr is None:
        # If there is no value on the protocol's attribute then the type hint is used directly. In this case,
        # only str, int, and float should really be handled, since all other types, will have more ambiguous
        # (de)serialization semantics that needs to be explicitly defined.
        if type_hint == str:
            return ""
        elif type_hint in (int, float):
            return "str"
        else:
            raise RuntimeError(
                "Only str, int, and float are directly supported for column schemas. For other types, define the schema via SchemaDescriptors."
            )
    elif isinstance(attr, SchemaDescriptor):
        return attr.serialize_codegen(namespace)

    raise RuntimeError(
        "Attributes for column schemas must either be unassigned (None) or a SchemaDescriptor."
    )


def compile_token_parser[S: TokenProtocol](s: type[S]) -> Callable[[str], S]:
    hints = get_type_hints(s)

    field_names: list[str] = []
    field_irs: list[str] = []
    conll_irs: list[str] = []
    namespace = {s.__name__: s, "ParseError": ParseError, "Conllable": Conllable}

    for i, (name, type_hint) in enumerate(hints.items()):
        field_names.append(name)
        attr = getattr(s, name) if hasattr(s, name) else None

        deserialize_name = compile_deserialize_schema_ir(namespace, attr, type_hint)
        field_ir = f"{name} = {deserialize_name}(fields[{i}])"
        field_irs.append(field_ir)

        serialize_name = compile_serialize_schema_ir(namespace, attr, type_hint)
        conll_ir = f"{name} = {serialize_name}(self.{name})"
        conll_irs.append(conll_ir)

    unique_token_name = unique_name_id("Token")
    class_ir = root_ir(
        f"""
        class {unique_token_name}({s.__name__}):
            __slots__ = (\"{"\", \"".join(field_names)}\",)

            def __init__(self, {", ".join(field_names)}) -> None:
                {"\n                ".join(f"self.{fn} = {fn}" for fn in field_names)}

            def conll(self) -> str:
                {"\n                ".join(conll_irs)}
                items = [{", ".join(field_names)}]
                return "\\t".join(items)
        """
    )
    exec(class_ir, namespace)

    compiled_parse_token = unique_name_id("compiled_parse_token")
    compiled_parse_token_ir = root_ir(
        f"""
        def {compiled_parse_token}(line: str) -> {s.__name__}:
            fields = line.split("\\t")

            if len(fields) != {len(field_names)}:
                error_msg = f"The number of columns per token line must be {len(field_names)}. Invalid token: {{line!r}}"
                raise ParseError(error_msg)

            if len(fields[-1]) > 0 and fields[-1][-1] == "\\n":
                fields[-1] = fields[-1][:-1]

            {"\n            ".join(field_irs)}

            return {unique_token_name}({",".join(field_names)})
        """
    )

    exec(compiled_parse_token_ir, namespace)
    parser = cast(Callable[[str], S], namespace[compiled_parse_token])
    return parser
