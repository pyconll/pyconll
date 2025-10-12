from dataclasses import dataclass, field
from typing import Callable, Optional, Protocol, TYPE_CHECKING, Union, Unpack

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparisonT

class FieldDescriptor: pass

@dataclass
class optional[T](FieldDescriptor):
    empty: str
    mapper: Optional[FieldDescriptor | Callable[[str], T]] = field(default=None, kw_only=True)

@dataclass
class mapping[K, V](FieldDescriptor):
    empty: str
    pair_delimiter: str
    av_delimiter: str
    kmapper: Optional[FieldDescriptor | Callable[[str], K]] = field(default=None, kw_only=True)
    vmapper: Optional[FieldDescriptor | Callable[[str], V]] = field(default=None, kw_only=True)
    ordering_key: Optional[FieldDescriptor | Callable[[K], SupportsRichComparisonT]] = field(default=None, kw_only=True)

@dataclass
class array_set[T](FieldDescriptor):
    delimiter: str
    el_mapper: Optional[FieldDescriptor | Callable[[str], T]] = field(default=None, kw_only=True)

@dataclass
class array_tuple[*Ts](FieldDescriptor):
    delimiter: str
    el_mapper: Optional[FieldDescriptor | Callable[[int, str], Union[Unpack[*Ts]]]] = field(default=None, kw_only=True)

class ConlluToken(Protocol):
    id: str
    form: Optional[str] = optional[str]('_')
    lemma: Optional[str] = optional[str]('_')
    upos: Optional[str] = optional[str]('_')
    xpos: Optional[str] = optional[str]('_')
    feats: dict[str, set[str]] = mapping[str, set[str]](
        '_', '|', '=',
        vmapper=array_set(','),
        ordering_key=lambda k: k.lower())
    head: Optional[str] = optional[str]('_')
    deprel: Optional[str] = optional[str]('_')
    deps: dict[str, tuple[str, str, str, str]] = mapping[str, tuple[str, str, str, str]](
        '_', '|', ':',
        vmapper=array_tuple[str, str, str, str](':'))
    misc: dict[str, Optional[set[str]]] = mapping[str, Optional[set[str]]](
        '_', '|', '=',
        vmapper=optional('_', mapper=array_set[str](',')),
        ordering_key=lambda k: k.lower())

    def is_multiword(self) -> bool:
        """
        Checks if this Token is a multiword token.

        Returns:
            True if this token is a multiword token, and False otherwise.
        """
        return '-' in self.id

    def is_empty_node(self) -> bool:
        """
        Checks if this Token is an empty node, used for ellipsis annotation.

        Note that this is separate from any field being empty, rather it means
        the id has a period in it.

        Returns:
            True if this token is an empty node and False otherwise.
        """
        return '.' in self.id