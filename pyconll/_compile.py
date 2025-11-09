# mypy: disable-error-code="misc"

"""
Module for compiling TokenSchema definitions into efficient parser and serializer functions.
"""

import re
from typing import Any, Callable, Optional, cast, get_type_hints

from pyconll.exception import FormatError, ParseError
from pyconll._ir import unique_name_id, process_ir
from pyconll.schema import _VarColsDescriptor, FieldDescriptor, TokenSchema


def _compile_deserialize_schema_ir(
    namespace: dict[str, Any], attr: Optional[FieldDescriptor], type_hint: type
) -> str:
    if attr is None:
        # If there is no value on the protocol's attribute then the type hint is used directly. In
        # this case, only str, int, and float should really be handled, since all other types, will
        # have more ambiguous (de)serialization semantics that needs to be explicitly defined.
        if type_hint == str:
            return ""
        if type_hint == int:
            return "int"
        if type_hint == float:
            return "float"

        raise RuntimeError(
            "Only str, int, and float are directly supported for column schemas. For other types, "
            "define the field via FieldDescriptors."
        )

    if isinstance(attr, FieldDescriptor):
        return attr.deserialize_codegen(namespace)

    raise RuntimeError(
        "Attributes for column schemas must either be unassigned (None) or a FieldDescriptor."
    )


def _compile_serialize_schema_ir(
    namespace: dict[str, Any], attr: Optional[FieldDescriptor], type_hint: type
) -> str:
    if attr is None:
        # If there is no value on the protocol's attribute then the type hint is used directly. In
        # this case, only str, int, and float should really be handled, since all other types, will
        # have more ambiguous (de)serialization semantics that needs to be explicitly defined.
        if type_hint == str:
            return ""
        if type_hint in (int, float):
            return "str"

        raise RuntimeError(
            "Only str, int, and float are directly supported for column schemas. For other types, "
            "define the field via FieldDescriptors."
        )

    if isinstance(attr, FieldDescriptor):
        return attr.serialize_codegen(namespace)

    raise RuntimeError(
        "Attributes for column schemas must either be unassigned (None) or a FieldDescriptor."
    )


def token_parser[S: TokenSchema](s: type[S], delimiter: str, collapse: bool) -> Callable[[str], S]:
    """
    Compile a TokenSchema definition into a method that can parse a given line of it.

    Args:
        s: The type to perform the compilation on.
        delimiter: The delimiter that separates the columsn of the lines.
        collapse: Flag if delimiters that are next to each other should be collapsed for the
            purposes of separating columns.

    Returns:
        The compiled method which can parse a string representation according to the Token
        definition.
    """
    hints = get_type_hints(s)

    field_names: list[str] = list(hints.keys())
    namespace = {
        s.__name__: s,
        "ParseError": ParseError,
    }

    unique_token_name = unique_name_id(namespace, "Token")
    class_ir = process_ir(
        t"""
        class {unique_token_name}({s.__name__}):
            __slots__ = (\"{"\", \"".join(field_names)}\",)

            def __init__(self, {", ".join(field_names)}) -> None:
                {"\n                ".join(f"self.{fn} = {fn}" for fn in field_names)}

            def __repr__(self) -> str:
                return f"{s.__name__}({", ".join([f"{{self.{fn}!r}}" for fn in field_names])})"
        """
    )
    exec(class_ir, namespace)  # pylint: disable=exec-used

    has_var_cols = False
    field_irs: list[str] = []
    for i, (name, type_hint) in enumerate(hints.items()):
        attr = getattr(s, name) if hasattr(s, name) else None

        # This is pretty messy, since the function prototype for each descriptor type leaks through
        # to this layer now, but changing it would require many more changes, so for now, keep this
        # approach.
        deserialize_name = _compile_deserialize_schema_ir(namespace, attr, type_hint)
        if isinstance(attr, _VarColsDescriptor):
            if has_var_cols:
                raise RuntimeError("Invalid TokenSchema with more than one varcols field.")

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
        length_guard = (t"if len(cols) < {(len(field_names) - 1, int)}: raise ParseError(f'The "
                        t"number of columns per token line must be at least "
                        t"{(len(field_names), int)}. Invalid token: {{line!r}}')")
    else:
        var_cols_ir = t""
        length_guard = (t"if len(cols) != {(len(field_names), int)}: raise ParseError(f'The number "
                        t"of columns per token line must be {(len(field_names), int)}. Invalid "
                        t"token: {{line!r}}')")

    if collapse:
        c = re.escape(delimiter) + "+"
        cols_ir = t"cols = re.split({c!r}, line)"
    else:
        cols_ir = t"cols = line.split({delimiter!r})"

    compiled_parse_token = unique_name_id(namespace, "compiled_parse_token")
    parser_ir = process_ir(
        t"""
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
            { "new_token.__post_init()" if hasattr(s, "__post_init") else "" }
            return new_token
        """
    )
    exec(parser_ir, namespace)  # pylint: disable=exec-used

    parser = cast(Callable[[str], S], namespace[compiled_parse_token])

    return parser

def token_serializer[S: TokenSchema](s: type[S], delimiter: str) -> Callable[[S], str]:
    """
    Compile a TokenSchema definition into a method that can serialize an instance.

    Args:
        s: The type to perform the serialization compilation on.
        delimiter: The delimiter to put between columns.

    Returns:
        The compiled method which can convert an instance of a Token schema into a string
        representation.
    """
    hints = get_type_hints(s)

    conll_irs: list[str] = []
    namespace = {
        s.__name__: s,
        "FormatError": FormatError,
    }

    for name, type_hint in hints.items():
        attr = getattr(s, name) if hasattr(s, name) else None

        serialize_name = _compile_serialize_schema_ir(namespace, attr, type_hint)
        if isinstance(attr, _VarColsDescriptor):
            conll_ir = f"cols.extend({serialize_name}(token.{name}))"
        else:
            conll_ir = f"cols.append({serialize_name}(token.{name}))"
        conll_irs.append(conll_ir)

    serialize_token = unique_name_id(namespace, "serialize_token")
    serializer_ir = process_ir(
        t"""
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
