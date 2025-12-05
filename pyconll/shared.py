"""
Contains definitions for concepts that are shared among many CoNLL variations.
"""

from typing import Optional, OrderedDict

from pyconll.schema import AbstractSentence


class Sentence[T](AbstractSentence[T]):
    """
    A very basic sentence type that can be used for most use cases. It simply stores the metadata
    and tokens in the order they were received. It can be used as a base level for other sentence
    implementations which want to add additional operations on top of this very common logic.
    """

    __slots__ = ("meta", "tokens")

    def __init__(self) -> None:
        """
        Create a new structured Sentence object.
        """
        self.meta: OrderedDict[str, Optional[str]] = OrderedDict[str, Optional[str]]()
        self.tokens: list[T] = []

    def __accept_meta__(self, key: str, value: Optional[str]) -> None:
        """
        Accept the next metadata values.

        Args:
            key: The key of the metadata.
            value: The value of the metadata or None if it is a singleton.
        """
        self.meta[key] = value

    def __accept_token__(self, t: T) -> None:
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
