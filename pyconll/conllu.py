"""
Defines the Token type and parsing and output logic. A Token is the based unit in CoNLL-U and so the
data and parsing in this module is central to the CoNLL-U format.
"""

import functools
import math
import sys
from typing import Optional, OrderedDict

from pyconll import tree
from pyconll.format import Format
from pyconll.schema import (
    FieldDescriptor,
    SentenceBase,
    mapping_ext,
    nullable,
    mapping,
    tokenspec,
    unique_array,
    fixed_array,
    via,
)
from pyconll.tree import Tree


@functools.total_ordering
class _TokenIdComparer:
    """
    Implementation class for comparing token ids to be sorted, using the
    standard python sorting routines. Two ids are equal if the id text is
    exactly the same. Otherwise, ids are compared by parts, with a range id
    being compared by the start index and then by the end index, and decimal
    ids having the radix separated parts compared separately.
    """

    def __init__(self, token_id):
        """
        Create the comparer wrapping the given, assumed valid format, id.

        Args:
            token_id: The token id to wrap.
        """
        self.token_id = token_id

    def __eq__(self, other):
        """
        Compares if the current id is equal to the provided id.

        Args:
            other: The other id wrapper to compare against.

        Returns:
            True if the two underlying ids are exactly the same.
        """
        return self.token_id == other.token_id

    def __ne__(self, other):
        """
        Compares if the current id is not equal to the provided id.

        Args:
            other: The other id wrapper to compare against.

        Returns:
            True if the two underlying ids are not the same.
        """
        return not self == other

    @staticmethod
    def _split_token_id_as_range(token_id):
        """
        Splits a token into its individual parts as a range.

        If the token does not represent a range, the beginning and end are the
        same token id.

        Args:
            token_id: The id to split into its range parts.

        Returns:
            A tuple of size two with the token id representing the range.
        """
        idx = token_id.find("-")
        if idx < 0:
            return (token_id, token_id)

        return (token_id[:idx], token_id[idx + 1 :])

    @staticmethod
    def _split_by_radix(token_id):
        """
        Split a non-range token id by the radix point.

        Any id without a radix point will assume it is 0.

        Args:
            token_id: The id to decompose into its two parts based on the radix.

        Returns:
            A tuple of size 2 with the id parts decomposed as integers.
        """
        idx = token_id.find(".")
        if idx < 0:
            return [int(token_id), 0]

        first = int(token_id[:idx])
        second = int(token_id[idx + 1 :])
        return [first, second]

    @staticmethod
    def _cmp_individual_ids(a, b):
        """
        Compare two non-range token ids using a traditional compare function.

        Args:
            a: The first argument to compare and the basis of the comparison.
            b: The second argument to compare against.

        Returns:
            The results of a traditional compare function in basis of a to b.
        """
        a_l, a_r = _TokenIdComparer._split_by_radix(a)
        b_l, b_r = _TokenIdComparer._split_by_radix(b)

        return _TokenIdComparer._zcopysign(2, a_l - b_l) + _TokenIdComparer._zcopysign(1, a_r - b_r)

    @staticmethod
    def _zcopysign(a, b):
        """
        copysign that returns the sign indicator if it is 0 or -0.

        Args:
            a: The magnitude.
            b: The sign indicator.

        Returns:
            Usual copysign result unless sign indicator is 0.
        """
        if not b:
            return b

        return math.copysign(a, b)

    def __lt__(self, other):
        """
        Compares if other is less than the currently wrapped id.

        Args:
            other: The wrapped id to compare against.

        Returns:
            True if the current id is less than the id wrapped by other.
        """
        self_split_1, self_split_2 = _TokenIdComparer._split_token_id_as_range(self.token_id)
        other_split_1, other_split_2 = _TokenIdComparer._split_token_id_as_range(other.token_id)

        first_cmp = _TokenIdComparer._cmp_individual_ids(self_split_1, other_split_1)

        return first_cmp < 0 or (
            first_cmp == 0 and _TokenIdComparer._cmp_individual_ids(self_split_2, other_split_2)
        )


@tokenspec(slots=True, gen_repr=True)
class Token:
    """
    The base Token definition which will be used for both the Standard and Compact implementations.

    This defines the attributes and any behavior on the CoNLL-U data model.
    """

    id: str
    form: Optional[str]
    lemma: Optional[str]
    upos: Optional[str]
    xpos: Optional[str]
    feats: dict[str, set[str]]
    head: Optional[str]
    deprel: Optional[str]
    deps: dict[str, tuple[str, ...]]
    misc: dict[str, Optional[set[str]]]

    def __post_init__(self) -> None:
        """
        Post-initialization logic beyond per-field serialization needed to properly create Token.

        Specifically, this handles the case where both the form and lemma are underscore in which
        case the behavior should be to treat these as their raw values.
        """
        if self.form is None and self.lemma is None:
            self.form = self.lemma = "_"

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


_nullable = nullable(str, "_")
_standard_token_fields: dict[str, Optional[FieldDescriptor]] = {
    "id": None,
    "form": _nullable,
    "lemma": _nullable,
    "upos": _nullable,
    "xpos": _nullable,
    "feats": mapping(
        str, unique_array(str, ",", "", str.lower), "|", "=", "_", lambda p: p[0].lower()
    ),
    "head": _nullable,
    "deprel": _nullable,
    "deps": mapping(str, fixed_array(str, ":"), "|", ":", "_", lambda p: _TokenIdComparer(p[0])),
    "misc": mapping_ext(
        str,
        unique_array(str, ",", "", str.lower),
        None,
        "|",
        "=",
        "_",
        lambda p: p[0].lower(),
    ),
}


_intern: FieldDescriptor[str] = via(sys.intern)
_intern_nullable: FieldDescriptor[Optional[str]] = nullable(_intern, "_")
_compact_token_fields: dict[str, Optional[FieldDescriptor]] = {
    "id": _intern,
    "form": _intern_nullable,
    "lemma": _intern_nullable,
    "upos": _intern_nullable,
    "xpos": _intern_nullable,
    "feats": mapping(
        _intern,
        unique_array(_intern, ",", "", str.lower),
        "|",
        "=",
        "_",
        lambda p: p[0].lower(),
    ),
    "head": _intern_nullable,
    "deprel": _intern_nullable,
    "deps": mapping(
        _intern,
        fixed_array(_intern, ":"),
        "|",
        ":",
        "_",
        lambda p: _TokenIdComparer(p[0]),
    ),
    "misc": mapping_ext(
        _intern,
        unique_array(_intern, ",", "", str.lower),
        None,
        "|",
        "=",
        "_",
        lambda p: p[0].lower(),
    ),
}


class Sentence(SentenceBase[Token]):
    """
    A sentence in a CoNLL-U file. A sentence consists of several components.

    First, are comments. Each sentence must have two comments per UD v2
    guidelines, which are sent_id and text. Comments are stored as a dict in
    the meta field. For singleton comments with no key-value structure, the
    value in the dict has a value of None.

    Note the sent_id field is also assigned to the id property, and the text
    field is assigned to the text property for usability, and their importance
    as comments. The text property is read only along with the paragraph and
    document id. This is because the paragraph and document id are not defined
    per Sentence but across multiple sentences. Instead, these fields can be
    changed through changing the metadata of the Sentences.

    Then comes the token annotations. Each sentence is made up of many token
    lines that provide annotation to the text provided. While a sentence usually
    means a collection of tokens, in this CoNLL-U sense, it is more useful to
    think of it as a collection of annotations with some associated metadata.
    Therefore the text of the sentence cannot be changed with this class, only
    the associated annotations can be changed.
    """

    __slots__ = ["meta", "tokens"]

    def __init__(self) -> None:
        """
        Create a new structured Sentence object.
        """
        self.meta: OrderedDict[str, Optional[str]] = OrderedDict[str, Optional[str]]()
        self.tokens: list[Token] = []

    def __accept_meta__(self, key: str, value: Optional[str]) -> None:
        """
        Accept the next metadata values.

        Args:
            key: The key of the metadata.
            value: The value of the metadata or None if it is a singleton.
        """
        self.meta[key] = value

    def __accept_token__(self, t: Token) -> None:
        """
        Accept the next token value.

        Args:
            t: The next token value for this Sentence to accept.
        """
        self.tokens.append(t)

    def __finalize__(self) -> None:
        """
        There is nothing to finalize for this Sentence type.
        """

    def __repr__(self) -> str:
        """
        Create a string that represents this Sentence object.

        Returns:
            The constructed string.
        """
        return f"Sentence(meta={self.meta!r}, tokens={self.tokens!r})"

    def to_tree(self) -> Tree[Token]:
        """
        Create a tree from the default, pre-defined CoNLL-U tokens.

        This follows the assumptions of the CoNLL-U format, such as that the root token has a parent
        id of "0", and that empty and multiword tokens do not participate in the underlying tree
        structure.

        Args:
            tokens: The token objects to create a tree structure from.

        Returns:
            The constructed Tree object.
        """

        def assert_val[K](val: Optional[K]) -> K:
            if val is None:
                raise ValueError("The value cannot be None here.")
            return val

        return tree.from_tokens(
            self.tokens,
            "0",
            lambda k: assert_val(k.id),
            lambda k: assert_val(k.head),
            lambda k: k.is_empty_node() or k.is_multiword(),
        )


conllu = Format(
    Token, Sentence, field_descriptors=_standard_token_fields
)  # pylint: disable=invalid-name
"""
The default Format instance which can handle CoNLL-U objects directly.
This provides both parsing and serialization capabilities in a single interface.
"""

compact_conllu = Format(
    Token, Sentence, field_descriptors=_compact_token_fields
)  # pylint: disable=invalid-name
"""
The Format instance which handles CoNLL-U but creates a more compact in-memory representation. This
comes at a slight runtime penalty, but in practice the memory used is X% less. This instance
provides both parsing and serialization capabilities in a single interface.
"""

type ConlluFormat = Format[Token, Sentence]
