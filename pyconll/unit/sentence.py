"""
Defines the Sentence type and the associated parsing and output logic.
"""

from collections import OrderedDict
from typing import Optional

from pyconll.schema import TokenProtocol


class Sentence[T: TokenProtocol]:
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

    def __init__(self, meta: OrderedDict[str, Optional[str]], tokens: list[T]) -> None:
        """
        Create a new structured Sentence object.

        In a future iteration of these updates, the ids_to_indexes parameter will be omitted in
        favor of a lifecycle based API where token and meta data parsing can be hooked into for
        inline data structure creation.

        Args:
            meta: The sentence metadata. Kept in modification order.
            tokens: The tokens that make up this Sentence.
        """
        self.meta = meta
        self.tokens = tokens

    def __repr__(self) -> str:
        """
        Create a string that represents this Sentence object.

        Returns:
            The constructed string.
        """
        return f"Sentence(meta={self.meta!r}, tokens={self.tokens!r})"
