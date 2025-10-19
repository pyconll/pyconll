from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    cast,
    get_type_hints,
    Optional,
    TYPE_CHECKING,
)

from pyconll.conllable import Conllable
from pyconll.exception import FormatError, ParseError
from pyconll._ir import root_ir, unique_name_id

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison


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


def _deserialize_sub_method_name[T](
    namespace: dict[str, Any], mapper: type[T] | SchemaDescriptor[T]
) -> str:
    if isinstance(mapper, SchemaDescriptor):
        return mapper.deserialize_codegen(namespace)

    if mapper in (int, float):
        return mapper.__name__

    if mapper == str:
        return ""

    raise RuntimeError("Mapper must map via an int, float, or str or a nested SchemaDescriptor.")


def _serialize_sub_method_name[T](
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
    empty_marker: str

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = _deserialize_sub_method_name(namespace, self.mapper)
        return root_ir(
            f"""
            def {method_name}(s):
                if s == {self.empty_marker!r}:
                    return None
                return {sub_method_name}(s)
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = _serialize_sub_method_name(namespace, self.mapper)
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
        sub_method_name = _deserialize_sub_method_name(namespace, self.mapper)
        if not sub_method_name:
            result_ir = f"s.split({self.delimiter!r})"
        else:
            result_ir = f"[{sub_method_name}(el) for el in s.split({self.delimiter!r})]"

        return root_ir(
            f"""
            def {method_name}(s):
                if s == {self.empty_marker!r} or not s:
                    return []
                return {result_ir}
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = _serialize_sub_method_name(namespace, self.mapper)
        if not sub_method_name:
            gen_ir = "vs"
        else:
            gen_ir = f"{sub_method_name}(el) for el in vs"

        return root_ir(
            f"""
            def {method_name}(vs):
                if {self.empty_marker!r} != None and not vs:
                    return {self.empty_marker!r}
                return {self.delimiter!r}.join({gen_ir})
            """
        )


@dataclass(frozen=True, slots=True)
class _UniqueArrayDescriptor[T](SchemaDescriptor[set[T]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    empty_marker: Optional[str]
    ordering_key: Optional[Callable[[T], "SupportsRichComparison"]]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = _deserialize_sub_method_name(namespace, self.mapper)
        if not sub_method_name:
            return_ir = f"set(s.split({self.delimiter!r}))"
        else:
            return_ir = f"{{ {sub_method_name}(el) for el in s.split({self.delimiter!r}) }}"

        return root_ir(
            f"""
            def {method_name}(s):
                if s == {self.empty_marker!r} or not s:
                    return set()
                return {return_ir}
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = _serialize_sub_method_name(namespace, self.mapper)

        if self.ordering_key is None:
            values_ir = "vs"
        else:
            ordering_key_id = unique_name_id("_UniqueArrayDescriptor_ordering_key")
            namespace[ordering_key_id] = self.ordering_key
            values_ir = f"sorted(vs, key={ordering_key_id})"

        if not sub_method_name:
            gen_ir = values_ir
        else:
            gen_ir = f"{sub_method_name}(el) for el in {values_ir}"

        return root_ir(
            f"""
            def {method_name}(vs):
                if {self.empty_marker!r} != None and not vs:
                    return {self.empty_marker!r}
                
                return {self.delimiter!r}.join({gen_ir})
            """
        )


@dataclass(frozen=True, slots=True)
class _FixedArrayDescriptor[T](SchemaDescriptor[tuple[T, ...]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str
    empty_marker: Optional[str]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = _deserialize_sub_method_name(namespace, self.mapper)
        if not sub_method_name:
            gen_ir = f"s.split({self.delimiter!r})"
        else:
            gen_ir = f"{sub_method_name}(el) for el in s.split({self.delimiter!r})"

        return root_ir(
            f"""
            def {method_name}(s):
                if s == {self.empty_marker!r} or not s:
                    return ()

                return tuple({gen_ir})
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = _serialize_sub_method_name(namespace, self.mapper)
        if not sub_method_name:
            gen_ir = "tup"
        else:
            gen_ir = f"{sub_method_name}(el) for el in tup"

        return root_ir(
            f"""
            def {method_name}(tup):
                if {self.empty_marker!r} != None and not tup:
                    return {self.empty_marker!r}

                return {self.delimiter!r}.join({gen_ir})
            """
        )


@dataclass(frozen=True, slots=True)
class _LegacyFixedArrayDescriptor[T](SchemaDescriptor[tuple[T, T, T, T]]):
    mapper: type[T] | SchemaDescriptor[T]
    delimiter: str

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = _deserialize_sub_method_name(namespace, self.mapper)
        if sub_method_name != "":
            els_ir = f"[{sub_method_name}(el) for el in s.split({self.delimiter!r})]"
        else:
            els_ir = f"s.split({self.delimiter!r})"

        return root_ir(
            f"""
            def {method_name}(s):
                els = {els_ir}

                if 0 <= len(els) <= 4:
                    return tuple(els + ([None] * (4 - len(els))))

                msg = (f"Error parsing \\"{{s}}\\" as tuple properly. Please check against CoNLL "
                        "format spec.")
                raise ParseError(msg)
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        sub_method_name = _serialize_sub_method_name(namespace, self.mapper)

        return root_ir(
            f"""
            def {method_name}(tup):
                presents = list(filter(lambda el: el is not None, tup))
                if not presents:
                    raise FormatError("All values in the tuple are None.")

                gen_expr = ({sub_method_name}(el) for el in tup if el is not None)
                return {self.delimiter!r}.join(gen_expr)
            """
        )


@dataclass(frozen=True, slots=True)
class _MappingDescriptor[K, V](SchemaDescriptor[dict[K, V]]):
    kmapper: type[K] | SchemaDescriptor[K]
    vmapper: type[V] | SchemaDescriptor[V]
    pair_delimiter: str
    av_delimiter: str
    empty_marker: Optional[str]
    ordering_key: Optional[Callable[[tuple[K, V]], "SupportsRichComparison"]]
    use_compact_pair: bool

    # TODO: If the entire pair is empty, then also a flag should be added to say if that is treated
    # as an empty string to both mappers (although this seems not necessary for compatbility,
    # although test needs to be added to confirm stability of parsing). Although, this is similar to
    # emptiness handling and has multiple dimensions that could be addressed, such as NotCompact,
    # AllowCompactV, AllowCompactKV

    # And for reference emptiness handling needs to be a three part struct as well, which describes:
    #   empty_marker
    #   exclusive_marker

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        key_sub_method_name = _deserialize_sub_method_name(namespace, self.kmapper)
        value_sub_method_name = _deserialize_sub_method_name(namespace, self.vmapper)
        return root_ir(
            f"""
            def {method_name}(s):
                if s == {self.empty_marker!r} or not s:
                    return {{}}

                d = {{}}
                pairs = s.split({self.pair_delimiter!r})
                for pair in pairs:
                    avs = pair.split({self.av_delimiter!r}, 1)
                    if len(avs) == 1:
                        if {self.use_compact_pair!r}:
                            avs.append("")
                        else:
                            raise ParseError(f"Could not parse one of the pairs in {{s}} which did not have an attribute-value delimiter.")

                    d[{key_sub_method_name}(avs[0])] = {value_sub_method_name}(avs[1])

                return d
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        key_sub_method_name = _serialize_sub_method_name(namespace, self.kmapper)
        value_sub_method_name = _serialize_sub_method_name(namespace, self.vmapper)

        if self.ordering_key is not None:
            ordering_key_id = unique_name_id("_MappingDescriptor_ordering_key")
            namespace[ordering_key_id] = self.ordering_key
            items_ir = f"items = sorted(mapping.items(), key={ordering_key_id})"
        else:
            items_ir = "items = mapping.items()"

        return root_ir(
            f"""
            def {method_name}(mapping):
                if {self.empty_marker!r} != None and not mapping:
                    return {self.empty_marker!r}

                {items_ir}
                transformed = []
                for (key, value) in items:
                    value_str = {value_sub_method_name}(value)
                    if {self.use_compact_pair!r} and value_str == "":
                        transformed.append(({key_sub_method_name}(key),))
                    else:
                        transformed.append(({key_sub_method_name}(key), value_str))
                return {self.pair_delimiter!r}.join({self.av_delimiter!r}.join(t) for t in transformed)
            """
        )


@dataclass(frozen=True, slots=True)
class _CustomDescriptor[T](SchemaDescriptor[T]):
    deserialize: Callable[[str], T]
    serialize: Callable[[T], str]

    def do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        var_name = unique_name_id("_CustomDescriptor_Deserializer")
        namespace[var_name] = self.deserialize

        return root_ir(
            f"""
            def {method_name}(s):
                return {var_name}(s)
            """
        )

    def do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> str:
        var_name = unique_name_id("_CustomDescriptor_Serializer")
        namespace[var_name] = self.serialize

        return root_ir(
            f"""
            def {method_name}(s):
                return {var_name}(s)
            """
        )


def nullable[T](
    mapper: type[T] | SchemaDescriptor[T], empty_marker: str = ""
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


def legacy_fixed_array[T](
    mapper: type[T] | SchemaDescriptor[T], delimiter: str
) -> _LegacyFixedArrayDescriptor[T]:
    return _LegacyFixedArrayDescriptor[T](mapper, delimiter)


def mapping[K, V](
    kmapper: type[K] | SchemaDescriptor[K],
    vmapper: type[V] | SchemaDescriptor[V],
    pair_delimiter: str,
    av_delimiter: str,
    empty_marker: Optional[str] = None,
    ordering_key: Optional[Callable[[tuple[K, V]], "SupportsRichComparison"]] = None,
    allow_no_av_delimiter: bool = False,
) -> _MappingDescriptor[K, V]:
    return _MappingDescriptor[K, V](
        kmapper,
        vmapper,
        pair_delimiter,
        av_delimiter,
        empty_marker,
        ordering_key,
        allow_no_av_delimiter,
    )


def custom[T](
    deserialize: Callable[[str], T], serialize: Callable[[T], str]
) -> _CustomDescriptor[T]:
    return _CustomDescriptor[T](deserialize, serialize)


def schema[T](desc: SchemaDescriptor[T]) -> T:
    return cast(T, desc)


class TokenProtocol(Conllable):
    pass


def _compile_deserialize_schema_ir(
    namespace: dict[str, Any], attr: Optional[SchemaDescriptor], type_hint: type
) -> str:
    if attr is None:
        # If there is no value on the protocol's attribute then the type hint is used directly. In this case,
        # only str, int, and float should really be handled, since all other types, will have more ambiguous
        # (de)serialization semantics that needs to be explicitly defined.
        if type_hint == str:
            return ""
        if type_hint == int:
            return "int"
        if type_hint == float:
            return "float"

        raise RuntimeError(
            "Only str, int, and float are directly supported for column schemas. For other types, "
            "define the schema via SchemaDescriptors."
        )

    if isinstance(attr, SchemaDescriptor):
        return attr.deserialize_codegen(namespace)

    raise RuntimeError(
        "Attributes for column schemas must either be unassigned (None) or a SchemaDescriptor."
    )


def _compile_serialize_schema_ir(
    namespace: dict[str, Any], attr: Optional[SchemaDescriptor], type_hint: type
) -> str:
    if attr is None:
        # If there is no value on the protocol's attribute then the type hint is used directly. In this case,
        # only str, int, and float should really be handled, since all other types, will have more ambiguous
        # (de)serialization semantics that needs to be explicitly defined.
        if type_hint == str:
            return ""
        if type_hint in (int, float):
            return "str"

        raise RuntimeError(
            "Only str, int, and float are directly supported for column schemas. For other types, "
            "define the schema via SchemaDescriptors."
        )

    if isinstance(attr, SchemaDescriptor):
        return attr.serialize_codegen(namespace)

    raise RuntimeError(
        "Attributes for column schemas must either be unassigned (None) or a SchemaDescriptor."
    )


def _compile_token_parser[S: TokenProtocol](s: type[S]) -> Callable[[str], S]:
    hints = get_type_hints(s)

    field_names: list[str] = []
    field_irs: list[str] = []
    conll_irs: list[str] = []
    namespace = {
        s.__name__: s,
        "ParseError": ParseError,
        "FormatError": FormatError,
        "Conllable": Conllable,
    }

    for i, (name, type_hint) in enumerate(hints.items()):
        field_names.append(name)
        attr = getattr(s, name) if hasattr(s, name) else None

        deserialize_name = _compile_deserialize_schema_ir(namespace, attr, type_hint)
        field_ir = f"{name} = {deserialize_name}(fields[{i}])"
        field_irs.append(field_ir)

        serialize_name = _compile_serialize_schema_ir(namespace, attr, type_hint)
        conll_ir = f"{name} = {serialize_name}(self.{name})"
        conll_irs.append(conll_ir)

    unique_token_name = unique_name_id("Token")
    class_ir = root_ir(
        f"""
        class {unique_token_name}({s.__name__}):
            __slots__ = (\"{"\", \"".join(field_names)}\",)

            def __init__(self, {", ".join(field_names)}) -> None:
                {"\n                ".join(f"self.{fn} = {fn}" for fn in field_names)}

            def __repr__(self) -> str:
                return f"{s.__name__}({", ".join([f"{{ self.{fn}!r }}" for fn in field_names])})"

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
        def {compiled_parse_token}(line):
            fields = line.split("\\t")

            if len(fields) != {len(field_names)}:
                error_msg = f"The number of columns per token line must be {len(field_names)}. Invalid token: {{line!r}}"
                raise ParseError(error_msg)

            if len(fields[-1]) > 0 and fields[-1][-1] == "\\n":
                fields[-1] = fields[-1][:-1]

            {"\n            ".join(field_irs)}

            new_token = {unique_token_name}({",".join(field_names)})
            { "new_token.post_init()" if hasattr(s, "post_init") else "" }
            return new_token
        """
    )

    exec(compiled_parse_token_ir, namespace)
    parser = cast(Callable[[str], S], namespace[compiled_parse_token])
    return parser
