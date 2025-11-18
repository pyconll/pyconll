# mypy: disable-error-code="misc"

"""
Module for compiling token specification definitions into efficient parser and serializer functions.
"""

import re
from typing import Any, Callable, Optional, cast, get_type_hints

from pyconll.exception import FormatError, ParseError
from pyconll._ir import unique_name_id, process_ir
from pyconll.schema import _SpecData, _VarColsDescriptor, FieldDescriptor


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
            "define the field via FieldDescriptors or add it as a primitive via @tokenspec."
        )

    if isinstance(attr, FieldDescriptor):
        return attr.deserialize_codegen(namespace)

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
            "define the field via FieldDescriptors or add it as a primitive via @tokenspec."
        )

    if isinstance(attr, FieldDescriptor):
        return attr.serialize_codegen(namespace)

    raise RuntimeError(
        "Attributes for column schemas must either be unassigned (None) or a FieldDescriptor."
    )


def _compile_token_sub_class[S](
    s: type[S], sub_class_name: str, slots: bool, field_names: list[str], namespace: dict[str, Any]
):

    slots_ir = t"""__slots__ = (\"{"\", \"".join(field_names)}\",)""" if slots else t""
    post_init_ir = t"self.__post_init__()" if hasattr(s, "__post_init__") else t""

    class_ir = process_ir(t"""
        class {sub_class_name}({s.__name__}):
            {slots_ir:t}

            def __init__(self, {", ".join(field_names)}) -> None:
                {"\n                ".join(f"self.{fn} = {fn}" for fn in field_names)}
                {post_init_ir:t}

            def __repr__(self) -> str:
                return f"{s.__name__}({", ".join([f"{{self.{fn}!r}}" for fn in field_names])})"
        """)
    exec(class_ir, namespace)  # pylint: disable=exec-used


def token_parser[S](s: type[S], delimiter: str, collapse: bool) -> Callable[[str], S]:
    """
    Compile a class definition into a method that can parse a given line of it.

    Args:
        s: The type to perform the compilation on.
        delimiter: The delimiter that separates the columns of the lines.
        collapse: Flag if delimiters that are next to each other should be collapsed for the
            purposes of separating columns.

    Returns:
        The compiled method which can parse a string representation according to the Token
        definition.
    """
    if not hasattr(s, "__pyc_spec_data"):
        raise RuntimeError("The type provided for compilation was not defined with @tokenspec.")
    spec_data: _SpecData = getattr(s, "__pyc_spec_data")

    namespace = {s.__name__: s, "ParseError": ParseError}
    for p in spec_data.primitive_types:
        namespace[p.__name__] = p

    if spec_data.slots:
        setattr(s, "__slots__", ())

    hints = get_type_hints(s)
    field_names: list[str] = list(hints.keys())

    unique_token_name = unique_name_id(namespace, "Token")
    _compile_token_sub_class(s, unique_token_name, spec_data.slots, field_names, namespace)

    has_var_cols = False
    field_irs: list[str] = []
    for i, (name, type_hint) in enumerate(hints.items()):
        attr = getattr(s, name) if hasattr(s, name) else None

        # This is pretty messy, since the function prototype for each descriptor type leaks through
        # to this layer now, but changing it would require many more changes, so for now, keep this
        # approach.
        deserialize_name = _compile_deserialize_schema_ir(
            namespace, spec_data.primitive_types, attr, type_hint
        )
        if isinstance(attr, _VarColsDescriptor):
            if has_var_cols:
                raise RuntimeError("Invalid Token specification with more than one varcols field.")

            has_var_cols = True
            field_ir = f"{name} = {deserialize_name}(islice(cols, {i}, {i} + var_cols_len))"
        else:
            if not has_var_cols:
                field_ir = f"{name} = {deserialize_name}(cols[{i}])"
            else:
                field_ir = f"{name} = {deserialize_name}(cols[{i} + var_cols_len - 1])"
        field_irs.append(field_ir)

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

    if collapse:
        c = re.escape(delimiter) + "+"
        cols_ir = t"cols = re.split({c!r}, line)"
    else:
        cols_ir = t"cols = line.split({delimiter!r})"

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
                {"\n                ".join(field_irs)}
            except ParseError as rexc:
                raise rexc
            except Exception as exc:
                raise ParseError("Unable to deserialize representation during Token "
                                 " construction.") from exc

            new_token = {unique_token_name}({",".join(field_names)})
            return new_token
        """)
    exec(parser_ir, namespace)  # pylint: disable=exec-used

    parser = cast(Callable[[str], S], namespace[compiled_parse_token])

    return parser


def token_serializer[S](s: type[S], delimiter: str) -> Callable[[S], str]:
    """
    Compile a class definition into a method that can serialize an instance.

    Args:
        s: The type to perform the serialization compilation on.
        delimiter: The delimiter to put between columns.

    Returns:
        The compiled method which can convert an instance of a Token schema into a string
        representation.
    """
    if not hasattr(s, "__pyc_spec_data"):
        raise RuntimeError("The type provided for compilation was not defined with @tokenspec.")
    spec_data: _SpecData = getattr(s, "__pyc_spec_data")

    namespace = {s.__name__: s, "FormatError": FormatError}
    for p in spec_data.primitive_types:
        namespace[p.__name__] = p

    conll_irs: list[str] = []
    hints = get_type_hints(s)
    for name, type_hint in hints.items():
        attr = getattr(s, name) if hasattr(s, name) else None

        serialize_name = _compile_serialize_schema_ir(
            namespace, spec_data.primitive_types, attr, type_hint
        )
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

    serializer = cast(Callable[[S], str], namespace[serialize_token])
    return serializer
