"""
Module for serializing tokens and sentences of different schemas.
"""

import io
from typing import Iterator

from pyconll.schema import TokenSchema, compile_token_serializer
from pyconll.sentence import Sentence


class Serializer[T: TokenSchema]:
    """
    The actual serializer which is responsible for translating in-memory representations back to a
    string representation.
    """

    def __init__(self, schema: type[T], comment_marker: str = "#", delimiter: str = "\t") -> None:
        """
        Create a new serializer for a given token type.

        Args:
            schema: The schema to use for serializing the in-memory representation.
            comment_marker: The prefix to use for comments or metadata.
            delimiter: The delimiter between Token columns.
        """
        self.serializer = compile_token_serializer(schema)
        self.comment_marker = comment_marker
        self.delimiter = delimiter

    def serialize_token(self, token: T) -> str:
        """
        Serialize a token to a string representation.

        Args:
            token: The token to serialize.

        Returns:
            The serialized representation of the token.
        """
        return self.serializer(token, self.delimiter)

    def serialize_sentence(self, sentence: Sentence[T]) -> str:
        """
        Serialize a Sentence to a string representation.

        Args:
            sentence: The sentence to serialize.

        Returns:
            The serialized representation of the sentence.
        """
        buffer = io.StringIO()
        self.write_sentence(sentence, buffer)
        return buffer.getvalue()

    def write_sentence(self, sentence: Sentence[T], writable: io.TextIOBase) -> None:
        """
        Write an individual sentence to an IO buffer.

        Note that the buffer always has a newline added at the end.

        Args:
            sentence: The sentence to write to the buffer.
            writable: The buffer to do the writing to.

        Raises:
            FormatError: If the serialization of a Token was unable to be performed.
        """
        for meta in sentence.meta.items():
            if meta[1] is not None:
                line = f"{self.comment_marker} {meta[0]} = {meta[1]}\n"
            else:
                line = f"{self.comment_marker} {meta[0]}\n"
            writable.write(line)

        for token in sentence.tokens:
            writable.write(self.serializer(token, self.delimiter))
            writable.write("\n")

    def write_corpus(self, corpus: Iterator[Sentence[T]], writable: io.TextIOBase) -> None:
        """
        Write out the entire corpus to the IO buffer.

        Args:
            corpus: The sequence of sentences to write out.
            writable: The IO buffer to write the sentences to.

        Raises:
            FormatError: If the serialization of a Token was unable to be performed.
        """
        for sentence in corpus:
            self.write_sentence(sentence, writable)
            writable.write("\n")
