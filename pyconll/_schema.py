from dataclasses import dataclass, field
import random
from typing import Any, Callable, get_type_hints, Optional, Protocol, Type, TYPE_CHECKING, Union

from pyconll.exception import ParseError

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparisonT

class FieldDescriptor[T]:
    pass

@dataclass
class opt[T](FieldDescriptor[T]):
    empty: str
    mapper: Optional[FieldDescriptor[T]] = field(default=None)


# TODO: dict or mapping if possible.
@dataclass
class mapping[K, V](FieldDescriptor[dict[K, V]]):
    empty: str
    pair_delimiter: str
    av_delimiter: str
    kmapper: Optional[FieldDescriptor[K]] = field(default=None)
    vmapper: Optional[FieldDescriptor[V]] = field(default=None)
    ordering_key: Optional[Callable[[K], "SupportsRichComparisonT"]] = field(
        default=None
    )


@dataclass
class array_set[T](FieldDescriptor[T]):
    delimiter: str
    el_mapper: Optional[FieldDescriptor[T]] = field(default=None)


@dataclass
class array_tuple[*Ts](FieldDescriptor[tuple[*Ts]]):
    delimiter: str
    el_mapper: Optional[FieldDescriptor[Union[*Ts]]] = field(
        default=None
    )


class ConlluToken(Protocol):
    id: str
    # form: Optional[str] = optional[str]("_")
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


def add_field_descriptor_method(namespace: dict[str, Any], descriptor: FieldDescriptor) -> str:
    method_name = unique_name_id("mfd")
    if isinstance(descriptor, opt):
        sub_method_name = ""
        template = descriptor.__orig_class__.__args__[0]
        if descriptor.mapper is not None:
            sub_method_name = add_field_descriptor_method(namespace, descriptor.mapper)
        elif template == int or template == float:
            sub_method_name = template.__name__
        elif template != str:
            raise RuntimeError("Optional must wrap an int, float, or str or provide a nested schema descriptor.")

        method_ir = f"""
def {method_name}(s):
    if s == "{descriptor.empty}":
        return None
    else:
        return {sub_method_name}(s)
"""
    elif isinstance(descriptor, mapping):
        pass
    elif isinstance(descriptor, array_set):
        sub_method_name = ""
        template = descriptor.__orig_class__.__args__[0]
        if descriptor.el_mapper is not None:
            sub_method_name = add_field_descriptor_method(namespace, descriptor.el_mapper)
        elif template == int or template == float:
            sub_method_name = template.__name__
        elif template != str:
            raise RuntimeError("array_set must wrap an int, float, or str or provide a nested schema descriptor.")

        method_ir = f"""
def {method_name}(s):
    return {{ {sub_method_name}(el) for el in s.split("{descriptor.delimiter}") }}
"""
    elif isinstance(descriptor, array_tuple):
        pass
    else:
        raise RuntimeError("The FieldDescriptor could not be transformed into IR.")

    exec(method_ir, namespace)
    return method_name


def compile_token_parser[S: Protocol](s: Type[S]) -> Callable[[str], S]:
    hints = get_type_hints(s)

    field_names = []
    field_ir = []
    attrs = []
    namespace = {s.__name__: s, "ParseError": ParseError, "attrs": attrs}

    for (i, (name, type_hint)) in enumerate(hints.items()):
        attr = getattr(s, name) if hasattr(s, name) else None

        if attr is None:
            # If there is no value on the protocol's attribute then the type hint is used directly. In this case,
            # only str, int, and float should really be handled, since all other types, will have more ambiguous
            # (de)serialization semantics that needs to be explicitly defined.
            if type_hint == str:
                ir = f"{name} = fields[{i}]"
            elif type_hint == int:
                ir = f"{name} = int(fields[{i}])"
            elif type_hint == float:
                ir = f"{name} = float(fields[{i}])"
            else:
                raise RuntimeError("Only str, int, and float are directly supported for column schemas. For other types, define the schema via FieldDescriptors.")
        elif isinstance(attr, FieldDescriptor):
            method_name = add_field_descriptor_method(namespace, attr)
            ir = f"{name} = {method_name}(fields[{i}])"
        else:
            raise RuntimeError("Attributes for column schemas must either be unassigned (None) or a FieldDescriptor.")

        field_names.append(name)
        field_ir.append(ir)
        attrs.append(attr)

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

    {"\n    ".join(field_ir)}

    return {unique_token_name}({",".join(field_names)})
"""

    exec(compiled_parse_token_ir, namespace)
    return namespace[compiled_parse_token]
