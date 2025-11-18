# mypy: disable-error-code="misc"

"""
Module for structural Token parsing schema components and building blocks.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import CodeType
from typing import (
    Any,
    Callable,
    Iterable,
    cast,
    Optional,
    TYPE_CHECKING,
    overload,
)

from pyconll._ir import unique_name_id, process_ir

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison


class FieldDescriptor[T](ABC):
    """
    Base class to represent the different types of descriptors that can be defined for the Token
    fields. Each descriptor needs to be able to dynamically generate the relevant python code for
    (de)serialization.
    """

    @abstractmethod
    def deserialize_codegen(self, namespace: dict[str, Any]) -> str:
        """
        Adds the deserialization method to the given namespace and returns the method name.

        Args:
            namespace: The codegen namespace to define the method in.

        Returns:
            The name of the method that was generated.
        """

    @abstractmethod
    def serialize_codegen(self, namespace: dict[str, Any]) -> str:
        """
        Adds the serialization method to the given namespace and returns the method name.

        Args:
            namespace: The codegen namespace to define the method in.

        Returns:
            The name of the method that was generated.
        """


class BaseFieldDescriptor[T](FieldDescriptor[T]):
    """
    A FieldDescriptor to use for most scenarios where the descriptor has to generate code or an
    actual method.
    """

    @abstractmethod
    def _do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        """
        The method that sub-classes need to implement to support deserialization code generation.

        The pattern relied on here is that a method with a caller provided name will be returned by
        the method, and this will be defined within the given namespace. So any dependent variables
        can be defined within this namespace as necessary.

        Args:
            namespace: The namespace that the code generation is done in.
            method_name: The name the method must have.

        Returns:
            The compiled python code that was generated for deserialization of this field.
        """

    @abstractmethod
    def _do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        """
        The method that sub-classes need to implement to support serialization code generation.

        Args:
            namespace: The namespace that code generation is done in.
            method_name: The name the generated method must have.

        Returns:
            The compiled python code that was generated for serialization of this field.
        """

    def deserialize_codegen(self, namespace: dict[str, Any]) -> str:
        """
        Adds the deserialization method to the given namespace and returns the method name.

        Args:
            namespace: The codegen namespace to define the method in.

        Returns:
            The name of the method that was generated.
        """
        method_name = unique_name_id(namespace, "deserialize_" + self.__class__.__name__)
        codegen = self._do_deserialize_codegen(namespace, method_name)
        exec(codegen, namespace)  # pylint: disable=exec-used
        return method_name

    def serialize_codegen(self, namespace: dict[str, Any]) -> str:
        """
        Adds the serialization method to the given namespace and returns the method name.

        Args:
            namespace: The codegen namespace to define the method in.

        Returns:
            The name of the method that was generated.
        """
        method_name = unique_name_id(namespace, "serialize_" + self.__class__.__name__)
        codegen = self._do_serialize_codegen(namespace, method_name)
        exec(codegen, namespace)  # pylint: disable=exec-used
        return method_name


def _deserialize_sub_method_name[T](
    namespace: dict[str, Any], mapper: type[T] | FieldDescriptor[T]
) -> str:
    if isinstance(mapper, FieldDescriptor):
        return mapper.deserialize_codegen(namespace)

    if mapper in (int, float):
        return mapper.__name__

    if mapper == str:
        return ""

    raise RuntimeError("Mapper must map via an int, float, or str or a nested FieldDescriptor.")


def _serialize_sub_method_name[T](
    namespace: dict[str, Any], mapper: type[T] | FieldDescriptor[T]
) -> str:
    if isinstance(mapper, FieldDescriptor):
        return mapper.serialize_codegen(namespace)

    if mapper in (int, float):
        return "str"

    if mapper == str:
        return ""

    raise RuntimeError("Mapper must map via an int, float, or str or a nested FieldDescriptor.")


@dataclass(frozen=True, slots=True)
class _NullableDescriptor[T](BaseFieldDescriptor[Optional[T]]):
    mapper: type[T] | FieldDescriptor[T]
    empty_marker: str

    def _do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        sub_method_name = _deserialize_sub_method_name(namespace, self.mapper)
        return process_ir(t"""
            def {method_name}(s):
                if s == {self.empty_marker!r}:
                    return None
                return {sub_method_name}(s)
            """)

    def _do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        sub_method_name = _serialize_sub_method_name(namespace, self.mapper)
        return process_ir(t"""
            def {method_name}(val):
                if val is None:
                    return {self.empty_marker!r}

                return {sub_method_name}(val)
            """)


@dataclass(frozen=True, slots=True)
class _ArrayDescriptor[T](BaseFieldDescriptor[list[T]]):
    mapper: type[T] | FieldDescriptor[T]
    delimiter: str
    empty_marker: str

    def _do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        sub_method_name = _deserialize_sub_method_name(namespace, self.mapper)
        if not sub_method_name:
            result_ir = t"s.split({self.delimiter!r})"
        else:
            result_ir = t"[{sub_method_name}(el) for el in s.split({self.delimiter!r})]"

        return process_ir(t"""
            def {method_name}(s):
                if s == {self.empty_marker!r}:
                    return []
                return {result_ir:t}""")

    def _do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        sub_method_name = _serialize_sub_method_name(namespace, self.mapper)
        if not sub_method_name:
            gen_ir = t"vs"
        else:
            gen_ir = t"{sub_method_name}(el) for el in vs"

        return process_ir(t"""
            def {method_name}(vs):
                if not vs:
                    return {self.empty_marker!r}
                return {self.delimiter!r}.join({gen_ir:t})""")


@dataclass(frozen=True, slots=True)
class _UniqueArrayDescriptor[T](BaseFieldDescriptor[set[T]]):
    mapper: type[T] | FieldDescriptor[T]
    delimiter: str
    empty_marker: str
    ordering_key: Optional[Callable[[T], "SupportsRichComparison"]]

    def _do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        sub_method_name = _deserialize_sub_method_name(namespace, self.mapper)
        if not sub_method_name:
            return_ir = t"set(s.split({self.delimiter!r}))"
        else:
            return_ir = t"{{ {sub_method_name}(el) for el in s.split({self.delimiter!r}) }}"

        return process_ir(t"""
            def {method_name}(s):
                if s == {self.empty_marker!r}:
                    return set()
                return {return_ir:t}""")

    def _do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        sub_method_name = _serialize_sub_method_name(namespace, self.mapper)

        if self.ordering_key is None:
            values_ir = t"vs"
        else:
            ordering_key_id = unique_name_id(namespace, "_UniqueArrayDescriptor_ordering_key")
            namespace[ordering_key_id] = self.ordering_key
            values_ir = t"sorted(vs, key={ordering_key_id})"

        if not sub_method_name:
            gen_ir = values_ir
        else:
            gen_ir = t"{sub_method_name}(el) for el in {values_ir:t}"

        return process_ir(t"""
            def {method_name}(vs):
                if not vs:
                    return {self.empty_marker!r}
                
                return {self.delimiter!r}.join({gen_ir:t})""")


@dataclass(frozen=True, slots=True)
class _FixedArrayDescriptor[T](BaseFieldDescriptor[tuple[T, ...]]):
    mapper: type[T] | FieldDescriptor[T]
    delimiter: str
    empty_marker: str

    def _do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        sub_method_name = _deserialize_sub_method_name(namespace, self.mapper)
        if not sub_method_name:
            gen_ir = t"s.split({self.delimiter!r})"
        else:
            gen_ir = t"{sub_method_name}(el) for el in s.split({self.delimiter!r})"

        return process_ir(t"""
            def {method_name}(s):
                if s == {self.empty_marker!r}:
                    return ()

                return tuple({gen_ir:t})""")

    def _do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        sub_method_name = _serialize_sub_method_name(namespace, self.mapper)
        if not sub_method_name:
            gen_ir = t"tup"
        else:
            gen_ir = t"{sub_method_name}(el) for el in tup"

        return process_ir(t"""
            def {method_name}(tup):
                if not tup:
                    return {self.empty_marker!r}

                return {self.delimiter!r}.join({gen_ir:t})""")


@dataclass(frozen=True, slots=True)
class _MappingDescriptor[K, V](BaseFieldDescriptor[dict[K, V]]):
    kmapper: type[K] | FieldDescriptor[K]
    vmapper: type[V] | FieldDescriptor[V]
    pair_delimiter: str
    kv_delimiter: str
    empty_marker: str
    ordering_key: Optional[Callable[[tuple[K, V]], "SupportsRichComparison"]]
    use_compact_pair: bool

    def _do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        key_sub_method_name = _deserialize_sub_method_name(namespace, self.kmapper)
        value_sub_method_name = _deserialize_sub_method_name(namespace, self.vmapper)
        return process_ir(t"""
            def {method_name}(s):
                if s == {self.empty_marker!r}:
                    return {{}}

                d = {{}}
                pairs = s.split({self.pair_delimiter!r})
                for pair in pairs:
                    avs = pair.split({self.kv_delimiter!r}, 1)
                    if len(avs) == 1:
                        if {(self.use_compact_pair, bool)!r}:
                            avs.append("")
                        else:
                            raise ParseError(f"Could not parse one of the pairs in {{s}} which did "
                                              "not have an attribute-value delimiter.")

                    d[{key_sub_method_name}(avs[0])] = {value_sub_method_name}(avs[1])

                return d
            """)

    def _do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        key_sub_method_name = _serialize_sub_method_name(namespace, self.kmapper)
        value_sub_method_name = _serialize_sub_method_name(namespace, self.vmapper)

        if self.ordering_key is not None:
            ordering_key_id = unique_name_id(namespace, "_MappingDescriptor_ordering_key")
            namespace[ordering_key_id] = self.ordering_key
            items_ir = t"items = sorted(mapping.items(), key={ordering_key_id})"
        else:
            items_ir = t"items = mapping.items()"

        return process_ir(t"""
            def {method_name}(mapping):
                if not mapping:
                    return {self.empty_marker!r}

                {items_ir:t}

                transformed = []
                for (key, value) in items:
                    value_str = {value_sub_method_name}(value)
                    if {(self.use_compact_pair, bool)!r} and value_str == "":
                        transformed.append(({key_sub_method_name}(key),))
                    else:
                        transformed.append(({key_sub_method_name}(key), value_str))
                gen_expr = ({self.kv_delimiter!r}.join(t) for t in transformed)
                return {self.pair_delimiter!r}.join(gen_expr)
            """)


@dataclass(frozen=True, slots=True)
class _VarColsDescriptor[T](BaseFieldDescriptor[list[T]]):
    mapper: type[T] | FieldDescriptor[T]

    def _do_deserialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        sub_method_name = _deserialize_sub_method_name(namespace, self.mapper)
        return process_ir(t"""
            def {method_name}(col_iter):
                return [{sub_method_name}(col) for col in col_iter]
            """)

    def _do_serialize_codegen(self, namespace: dict[str, Any], method_name: str) -> CodeType:
        sub_method_name = _serialize_sub_method_name(namespace, self.mapper)
        return process_ir(t"""
            def {method_name}(vals):
                return [{sub_method_name}(v) for v in vals]
            """)


@dataclass(frozen=True, slots=True)
class _ViaDescriptor[T](FieldDescriptor[T]):
    deserialize: Callable[[str], T]
    serialize: Callable[[T], str]

    def deserialize_codegen(self, namespace: dict[str, Any]) -> str:
        if self.deserialize is str:
            return ""

        if self.deserialize in (int, float):
            return self.deserialize.__name__

        name = unique_name_id(namespace, "_ViaDescriptor_Deserializer")
        namespace[name] = self.deserialize
        return name

    def serialize_codegen(self, namespace: dict[str, Any]) -> str:
        if self.serialize is str:
            return "str"

        if self.serialize is repr:
            return "repr"

        name = unique_name_id(namespace, "_ViaDescriptor_Serializer")
        namespace[name] = self.serialize
        return name


def nullable[T](
    mapper: type[T] | FieldDescriptor[T], empty_marker: str = ""
) -> _NullableDescriptor[T]:
    """
    Describe a serialization schema for an optional value.

    Args:
        mapper: The nested mapper to describe the serialization scheme of the underlying type.
        empty_marker: The string value which represents None.

    Returns:
        The FieldDescriptor to use for compiling the structural Token parser.
    """
    return _NullableDescriptor[T](mapper, empty_marker)


def array[T](
    el_mapper: type[T] | FieldDescriptor[T], delimiter: str, empty_marker: str = ""
) -> _ArrayDescriptor[T]:
    """
    Describe a serialization schema for a list.

    Args:
        mapper: The nested mapper to describe the serialization scheme of array elements.
        delimiter: The string which separates array elements in the serialized representation.
        empty_marker: The string representation which maps to an empty list.

    Returns:
        The FieldDescriptor to use for compiling the structural Token parser.
    """
    return _ArrayDescriptor[T](el_mapper, delimiter, empty_marker)


def unique_array[T](
    el_mapper: type[T] | FieldDescriptor[T],
    delimiter: str,
    empty_marker: str = "",
    ordering_key: Optional[Callable[[T], Any]] = None,
) -> _UniqueArrayDescriptor[T]:
    """
    Describe a serialization schema for a set.

    Args:
        el_mapper: The nested mapper to describe the serialization scheme of the set elements.
        delimiter: The string which separates set elements in the serialized representation.
        empty_marker: The string representation which maps to an empty set.
        ordering_key: If provided, describes the order in which the set entries are serialized.

    Returns:
        The FieldDescriptor to use for compiling the structural Token parser.
    """
    return _UniqueArrayDescriptor(el_mapper, delimiter, empty_marker, ordering_key)


def fixed_array[T](
    el_mapper: type[T] | FieldDescriptor[T],
    delimiter: str,
    empty_marker: str = "",
) -> _FixedArrayDescriptor[T]:
    """
    Describe a serialization schema for a tuple.

    Args:
        el_mapper: The nested mapper to describe the serialization scheme of the tuple elements.
        delimiter: The string which separates tuple elements in the serialized representation.
        empty_marker: The string representation which maps to an empty tuple.

    Returns:
        The FieldDescriptor to use for compiling the structural Token parser.
    """
    return _FixedArrayDescriptor[T](el_mapper, delimiter, empty_marker)


def mapping[K, V](
    kmapper: type[K] | FieldDescriptor[K],
    vmapper: type[V] | FieldDescriptor[V],
    pair_delimiter: str,
    kv_delimiter: str,
    empty_marker: str = "",
    ordering_key: Optional[Callable[[tuple[K, V]], "SupportsRichComparison"]] = None,
    use_compact_pair: bool = False,
) -> _MappingDescriptor[K, V]:
    """
    Describe a serialization scheme for a dictionary.

    Args:
        kmapper: The nested mapper to describe the serialization scheme for keys in the map.
        vmapper: The nested mapper to describe the serialization scheme for values in the map.
        pair_delimiter: The string to delimit key-value pairs in the serialized representation.
        kv_delimiter: The string to delimit the key and value within a single pair.
        empty_marker: The string representation which maps to an empty dict.
        ordering_key: If provided, describes the order in which the dict entries are serialized.
        use_compact_pair: A compact pair is one in which if the serialized value is an empty string
            then the key-value delimiter is not present. If set, this allows for compact pairs in
            deserialization and prefers compact pairs in serialization.

    Returns:
        The FieldDescriptor to use for compiling the structural Token parser.
    """
    return _MappingDescriptor[K, V](
        kmapper,
        vmapper,
        pair_delimiter,
        kv_delimiter,
        empty_marker,
        ordering_key,
        use_compact_pair,
    )


def varcols[T](mapper: type[T] | FieldDescriptor[T]) -> _VarColsDescriptor[T]:
    """
    Describe an entry that has a variable number of fields.

    Args:
        mapper: The nested mapper to describe the serialization schema for the targeted columns.

    Returns:
        The FieldDescriptor to use for compiling the structural Token parser.
    """
    return _VarColsDescriptor[T](mapper)


def via[T](deserialize: Callable[[str], T], serialize: Callable[[T], str]) -> _ViaDescriptor[T]:
    """
    Describe a user-provided serialization scheme which uses arbitrary callables.

    Other descriptors create symmetric (de)serialization schemes while this allows for asymmetric
    definitions (that is reading in one thing and writing out another). This is a possible feature
    that is not fully fleshed out, but could be better explored in the future.

    Args:
        deserialize: The callable to deserialize the string into the in-memory representation.
        serialize: The callable to serialize the in-memory representation to a string.

    Returns:
        The FieldDescriptor to use for compiling the structural Token parser.
    """
    return _ViaDescriptor[T](deserialize, serialize)


def field[T](desc: FieldDescriptor[T]) -> T:
    """
    Method to help with type-checking on structural Token definitions.

    Use on the outer-most level of each Token's field descriptor to unwrap the appropriate type.
    The only application of this method is on structural Token definitions.

    Args:
        desc: The FieldDescriptor whose type is being unwrapped.

    Returns:
        The descriptor originally provided by force cast to the type it describes.
    """
    return cast(T, desc)


@dataclass(frozen=True, slots=True)
class _SpecData:
    slots: bool
    extra_primitives: set[type]


@overload
def tokenspec[T: type](
    cls: T,
    /,
    *,
    slots: bool = False,
    extra_primitives: Optional[Iterable[type]] = None,
) -> T: ...


@overload
def tokenspec[T: type](
    cls: None = None,
    /,
    *,
    slots: bool = False,
    extra_primitives: Optional[Iterable[type]] = None,
) -> Callable[[T], T]: ...


def tokenspec(
    cls: Optional[type] = None,
    /,
    *,
    slots: bool = False,
    extra_primitives: Optional[Iterable[type]] = None,
) -> Callable[[type], type] | type:
    """
    Annotate a Token's class for different aspects.

    Args:
        cls: The class to decorate as a token specification.
        slots: Flag if the generated class should use slots for member storage.
        extra_primitives: Types that should be considered as "primitives" in addition to int, float,
            and str. What this means is that during compilation of parsing and serialization code,
            these types will construct the in-memory representations directly by the type
            constructor and the str operator will be for serialization.

    Returns:
        The decorated class instance that can be used with Format operations.
    """

    def decorator(cls: type) -> type:
        if hasattr(cls, "__pyconll_spec_data"):
            raise RuntimeError(f"@tokenspec was used already used on {cls.__name__}.")
        extra = set(extra_primitives) if extra_primitives else set()
        setattr(cls, "__pyconll_spec_data", _SpecData(slots, extra))
        return cls

    if cls is None:
        return decorator

    return decorator(cls)
