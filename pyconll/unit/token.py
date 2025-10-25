"""
Defines the Token type and parsing and output logic. A Token is the based unit
in CoNLL-U and so the data and parsing in this module is central to the CoNLL-U
format.
"""

import functools
import math
from typing import Optional

from pyconll.schema import (
    schema,
    nullable,
    mapping,
    unique_array,
    fixed_array,
    TokenProtocol,
    token_lifecycle,
)


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


def _conllu_post_init(t: "Token") -> None:
    """
    Post-initialization logic beyond per-field serialization needed to properly create Token.

    Specifically, this handles the case where both the form and the lemma are underscore in which
    case the behavior should be to treat these as their raw values.
    """
    if t._form is None and t.lemma is None:
        t._form = t.lemma = "_"


@token_lifecycle(post_init=_conllu_post_init)
class Token(TokenProtocol):
    """
    The prototypical CoNLL-U token definition. For reading CoNLL-U token files, use this as the
    Token schema. Similarly, if defining a different schema to read, use this as a reference for how
    this can be done.
    """

    id: str
    _form: Optional[str] = schema(nullable(str, "_"))
    lemma: Optional[str] = schema(nullable(str, "_"))
    upos: Optional[str] = schema(nullable(str, "_"))
    xpos: Optional[str] = schema(nullable(str, "_"))
    feats: dict[str, set[str]] = schema(
        mapping(str, unique_array(str, ",", "", str.lower), "|", "=", "_", lambda p: p[0].lower())
    )
    head: Optional[str] = schema(nullable(str, "_"))
    deprel: Optional[str] = schema(nullable(str, "_"))
    deps: dict[str, tuple[str, ...]] = schema(
        mapping(str, fixed_array(str, ":"), "|", ":", "_", lambda p: _TokenIdComparer(p[0]))
    )
    misc: dict[str, Optional[set[str]]] = schema(
        mapping(
            str,
            nullable(unique_array(str, ",", "", str.lower)),
            "|",
            "=",
            "_",
            lambda p: p[0].lower(),
            True,
        )
    )

    @property
    def form(self) -> Optional[str]:
        """
        Provide the word form of this Token. This property is read only.

        Returns:
            The Token form.
        """
        return self._form

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
