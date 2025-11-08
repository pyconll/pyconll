# mypy: disable-error-code="misc"

"""
Module for compiling TokenSchema definitions into efficient parser and serializer functions.
"""

from typing import Any, Callable, Optional, cast, get_type_hints

from pyconll.exception import FormatError, ParseError
from pyconll._ir import unique_name_id, process_ir
from pyconll.schema import FieldDescriptor, TokenSchema


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


def token_parser[S: TokenSchema](s: type[S]) -> Callable[[str, str], S]:
    """
    Compile a TokenSchema definition into a method that can parse a given line of it.

    Args:
        s: The type to perform the compilation on.

    Returns:
        The compiled method which can parse a string representation according to the Token
        definition.
    """
    hints = get_type_hints(s)

    field_names: list[str] = []
    field_irs: list[str] = []
    namespace = {
        s.__name__: s,
        "ParseError": ParseError,
    }

    for i, (name, type_hint) in enumerate(hints.items()):
        field_names.append(name)
        attr = getattr(s, name) if hasattr(s, name) else None

        deserialize_name = _compile_deserialize_schema_ir(namespace, attr, type_hint)
        field_ir = f"{name} = {deserialize_name}(fields[{i}])"
        field_irs.append(field_ir)

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

    compiled_parse_token = unique_name_id(namespace, "compiled_parse_token")
    parser_ir = process_ir(
        t"""
        def {compiled_parse_token}(line, delimiter):
            fields = line.split(delimiter)

            if len(fields) != {(len(field_names), int)}:
                raise ParseError(f"The number of columns per token line must be "
                                "{(len(field_names), int)}. Invalid token: {{line!r}}")

            if fields[-1].endswith("\\n"):
                fields[-1] = fields[-1][:-1]

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

    parser = cast(Callable[[str, str], S], namespace[compiled_parse_token])

    return parser

def token_serializer[S: TokenSchema](s: type[S]) -> Callable[[S, str], str]:
    """
    Compile a TokenSchema definition into a method that can serialize an instance.

    Args:
        s: The type to perform the serialization compilation on.

    Returns:
        The compiled method which can convert an instance of a Token schema into a string
        representation.
    """
    hints = get_type_hints(s)

    field_names: list[str] = []
    conll_irs: list[str] = []
    namespace = {
        s.__name__: s,
        "FormatError": FormatError,
    }

    for name, type_hint in hints.items():
        field_names.append(name)
        attr = getattr(s, name) if hasattr(s, name) else None

        serialize_name = _compile_serialize_schema_ir(namespace, attr, type_hint)
        conll_ir = f"{name} = {serialize_name}(token.{name})"
        conll_irs.append(conll_ir)

    serialize_token = unique_name_id(namespace, "serialize_token")
    serializer_ir = process_ir(
        t"""
        def {serialize_token}(token, delimiter) -> str:
            try:
                {"\n                ".join(conll_irs)}
                return f"{{ {'}\t{'.join(field_names)} }}"
            except FormatError as fexc:
                raise fexc
            except Exception as exc:
                raise FormatError(f"Unable to serialize Token: {{token!r}}.") from exc
        """)

    exec(serializer_ir, namespace)  # pylint: disable=exec-used

    serializer = cast(Callable[[S, str], str], namespace[serialize_token])
    return serializer
