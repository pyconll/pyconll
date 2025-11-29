# mypy: disable-error-code="misc"

"""
Module for compiling token specification definitions into efficient parser and serializer functions.
"""

import re
from typing import Any, Callable, Optional, cast, get_type_hints

from pyconll.exception import FormatError, ParseError
from pyconll._ir import unique_name_id, process_ir
from pyconll.schema import _SpecData, _VarColsDescriptor, FieldDescriptor

_deserialize_cache: dict[FieldDescriptor, tuple[str, Any]] = {}


def _compile_deserialize_schema_ir(
    namespace: dict[str, Any],
    extra_primitives: set[type],
    attr: Optional[FieldDescriptor],
    type_hint: type,
) -> str:
    if attr is None:
        # If there is no value on the protocol's attribute then the type hint is used directly. In
        # this case, only str, int, and float should really be handled, since all other types, will
        # have more ambiguous (de)serialization semantics that needs to be explicitly defined.
        if type_hint == str:
            return ""
        if type_hint in (int, float) or type_hint in extra_primitives:
            return type_hint.__name__

        raise RuntimeError(
            "Only str, int, and float are directly supported for column schemas. For other types, "
            "define the field via FieldDescriptors or register it as a primitive type."
        )

    if isinstance(attr, FieldDescriptor):
        if attr in _deserialize_cache:
            (old_name, old_method) = _deserialize_cache[attr]
            namespace[old_name] = old_method
            return old_name

        new_method_name = attr.deserialize_codegen(namespace)
        _deserialize_cache[attr] = (new_method_name, namespace[new_method_name])
        return new_method_name

    raise RuntimeError(
        "Attributes for column schemas must either be unassigned (None) or a FieldDescriptor."
    )


def _compile_serialize_schema_ir(
    namespace: dict[str, Any],
    extra_primitives: set[type],
    attr: Optional[FieldDescriptor],
    type_hint: type,
) -> str:
    if attr is None:
        # If there is no value on the protocol's attribute then the type hint is used directly. In
        # this case, only str, int, and float should really be handled, since all other types, will
        # have more ambiguous (de)serialization semantics that needs to be explicitly defined.
        if type_hint == str:
            return ""
        if type_hint in (int, float) or type_hint in extra_primitives:
            return "str"

        raise RuntimeError(
            "Only str, int, and float are directly supported for column schemas. For other types, "
            "define the field via FieldDescriptors or register it as a primitive type."
        )

    if isinstance(attr, FieldDescriptor):
        return attr.serialize_codegen(namespace)

    raise RuntimeError(
        "Attributes for column schemas must either be unassigned (None) or a FieldDescriptor."
    )


def token_parser[T](
    t: type[T],
    delimiter: str,
    collapse: bool = False,
    field_descriptors: Optional[dict[str, Optional[FieldDescriptor]]] = None,
    extra_primitives: Optional[set[type]] = None,
) -> Callable[[str], T]:
    """
    Compile a class definition into a method that can parse a given line of it.

    Args:
        t: The type to perform the compilation on.
        delimiter: The delimiter that separates the columns of the lines.
        collapse: Flag if delimiters that are next to each other should be collapsed for the
            purposes of separating columns.
        field_descriptors: Optional descriptor mapping from attribute name to descriptor to be used
            with precedence over type information if provided.
        extra_primitives: Any extra types which can use raw string construction and serialization.
            This takes precedence over what is given on the decorator.

    Returns:
        The compiled method which can parse a string representation according to the Token
        definition.
    """
    if not hasattr(t, "__pyconll_spec_data"):
        raise RuntimeError("The type provided for compilation was not defined with @tokenspec.")
    spec_data: _SpecData = getattr(t, "__pyconll_spec_data")
    extra_primitives = (
        extra_primitives if extra_primitives is not None else spec_data.extra_primitives
    )

    namespace = {p.__name__: p for p in extra_primitives}
    namespace.update({t.__name__: t, "ParseError": ParseError})

    hints = get_type_hints(t)
    field_names: list[str] = list(hints.keys())

    has_var_cols = False
    field_irs: list[str] = []
    for i, (name, type_hint) in enumerate(hints.items()):
        if field_descriptors is not None:
            attr = field_descriptors[name]
        else:
            attr = spec_data.fields.get(name, None)

        # This is pretty messy, since the function prototype for each descriptor type leaks through
        # to this layer now, but changing it would require many more changes, so for now, keep this
        # approach.
        deserialize_name = _compile_deserialize_schema_ir(
            namespace, extra_primitives, attr, type_hint
        )
        if isinstance(attr, _VarColsDescriptor):
            if has_var_cols:
                raise RuntimeError("Invalid Token specification with more than one varcols field.")

            has_var_cols = True
            field_ir = f"{deserialize_name}(islice(cols, {i}, {i} + var_cols_len))"
        else:
            if not has_var_cols:
                field_ir = f"{deserialize_name}(cols[{i}])"
            else:
                field_ir = f"{deserialize_name}(cols[{i} + var_cols_len - 1])"
        field_irs.append(field_ir)

    if collapse:
        c = re.escape(delimiter) + "+"
        cols_ir = t"cols = re.split({c!r}, line)"
    else:
        cols_ir = t"cols = line.split({delimiter!r})"

    if has_var_cols:
        var_cols_ir = t"var_cols_len = len(cols) - {(len(field_names), int)} + 1"
        length_guard = (
            t"if len(cols) < {(len(field_names) - 1, int)}: raise ParseError(f'The "
            t"number of columns per token line must be at least "
            t"{(len(field_names), int)}. Invalid token: {{line!r}}')"
        )
    else:
        var_cols_ir = t""
        length_guard = (
            t"if len(cols) != {(len(field_names), int)}: raise ParseError(f'The number "
            t"of columns per token line must be {(len(field_names), int)}. Invalid "
            t"token: {{line!r}}')"
        )

    compiled_parse_token = unique_name_id(namespace, "compiled_parse_token")
    parser_ir = process_ir(t"""
        from itertools import islice
        import re

        def {compiled_parse_token}(line):
            {cols_ir:t}
            {length_guard:t}
            {var_cols_ir:t}
            if cols[-1].endswith("\\n"):
                cols[-1] = cols[-1][:-1]

            try:
                return {t.__name__}({",".join(field_irs)})
            except ParseError as rexc:
                raise rexc
            except Exception as exc:
                raise ParseError("Unable to deserialize representation during Token"
                                 " construction.") from exc
        """)
    exec(parser_ir, namespace)  # pylint: disable=exec-used

    parser = cast(Callable[[str], T], namespace[compiled_parse_token])

    return parser


def token_serializer[T](
    t: type[T],
    delimiter: str,
    field_descriptors: Optional[dict[str, Optional[FieldDescriptor]]] = None,
    extra_primitives: Optional[set[type]] = None,
) -> Callable[[T], str]:
    """
    Compile a class definition into a method that can serialize an instance.

    Args:
        t: The type to perform the serialization compilation on.
        delimiter: The delimiter to put between columns.
        field_descriptors: Optional descriptor mapping from attribute name to descriptor to be used
            with precedence over type information if provided.
        extra_primitives: Any extra types which can use raw string construction and serialization.
            This takes precedence over what is given on the decorator.

    Returns:
        The compiled method which can convert an instance of a Token schema into a string
        representation.
    """
    if not hasattr(t, "__pyconll_spec_data"):
        raise RuntimeError("The type provided for compilation was not defined with @tokenspec.")
    spec_data: _SpecData = getattr(t, "__pyconll_spec_data")
    extra_primitives = (
        extra_primitives if extra_primitives is not None else spec_data.extra_primitives
    )

    namespace = {p.__name__: p for p in extra_primitives}
    namespace.update({t.__name__: t, "FormatError": FormatError})

    conll_irs: list[str] = []

    hints = get_type_hints(t)
    for name, type_hint in hints.items():
        if field_descriptors is not None:
            attr = field_descriptors[name]
        else:
            attr = spec_data.fields.get(name, None)

        serialize_name = _compile_serialize_schema_ir(namespace, extra_primitives, attr, type_hint)
        if isinstance(attr, _VarColsDescriptor):
            conll_ir = f"cols.extend({serialize_name}(token.{name}))"
        else:
            conll_ir = f"cols.append({serialize_name}(token.{name}))"
        conll_irs.append(conll_ir)

    serialize_token = unique_name_id(namespace, "serialize_token")
    serializer_ir = process_ir(t"""
        def {serialize_token}(token) -> str:
            try:
                cols = []
                {"\n                ".join(conll_irs)}
                return {delimiter!r}.join(cols)
            except FormatError as fexc:
                raise fexc
            except Exception as exc:
                raise FormatError(f"Unable to serialize Token: {{token!r}}.") from exc
        """)

    exec(serializer_ir, namespace)  # pylint: disable=exec-used

    serializer = cast(Callable[[T], str], namespace[serialize_token])
    return serializer
