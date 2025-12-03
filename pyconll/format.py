"""
Format module providing consolidated interfaces for CoNLL data parsing and serialization.

This module defines three classes:
- ReadFormat: For read-only parsing operations
- WriteFormat: For write-only serialization operations
- Format: Combines both reading and writing capabilities

For typical use cases where both read and write operations are needed, use Format.
For specialized read-only or write-only scenarios, use ReadFormat or WriteFormat directly.
"""

import io
import os
import string
from typing import Iterator, Optional

from pyconll import _compile
from pyconll.exception import ParseError
from pyconll.schema import AbstractSentence, FieldDescriptor
from pyconll.shared import Sentence

PathLike = str | bytes | os.PathLike


def _pair_down_whitespace(
    line: str, start_idx: int, end_idx: Optional[int] = None
) -> Optional[str]:
    """
    Remove whitespace from the delimited beginning and end regions of the string.

    Args:
        line: The string to remove whitespace from.
        start_idx: The location from which to start removing whitespace.
        end_idx: The location to move back from for removing whitespace. If not provided, it same as
            the length of the string.

    Returns:
        The string without whitespace surrounding it or None if the string was entirely whitespace.
    """
    end_idx = len(line) if end_idx is None else end_idx

    while start_idx < end_idx and line[start_idx] in string.whitespace:
        start_idx += 1

    if start_idx == end_idx:
        return None

    while (end_idx - 1) > start_idx and line[end_idx - 1] in string.whitespace:
        end_idx -= 1

    return line[start_idx:end_idx]


class ReadFormat[T, S: AbstractSentence]:
    """
    A read-only interface for parsing CoNLL formatted data.

    This class wraps Parser functionality and provides methods to parse CoNLL data
    from various sources including strings, files, and IO resources. Use this when
    only parsing operations are needed.
    """

    def __init__(
        self,
        token_schema: type[T],
        sentence_schema: type[S],
        comment_marker: str = "#",
        delimiter: str = "\t",
        collapse_delimiters: bool = False,
        field_descriptors: Optional[dict[str, Optional[FieldDescriptor]]] = None,
        extra_primitives: Optional[set[type]] = None,
    ) -> None:
        """
        Initialize the read format handler.

        Args:
            token_schema: The Token type to use for parsing.
            sentence_schema: The Sentence type to use for parsing.
            comment_marker: The character that marks the beginning of comments. Defaults to '#'.
            delimiter: The delimiter between the columns on a token line. Defaults to tab.
            collapse_delimiters: Flag if sequential delimiters denote an empty value or should be
                collapsed into one larger delimiter. Defaults to False.
            field_descriptors: The descriptors for the fields on the schema as a mapping from the
                field name to the descriptor instance. For primitive types, use None as the
                descriptor. This takes precedence over anything on the type itself.
            extra_primitives: The set of types to consider as primitives (default construction and
                the str() operator are appropriate). This takes precedence over what is given on the
                tokenspec decorator.
        """
        if len(comment_marker) != 1:
            raise ValueError("The comment marker is expected to only be one character.")

        self.comment_marker = comment_marker

        self.sentence_schema = sentence_schema
        self.token_parser = _compile.token_parser(
            token_schema, delimiter, collapse_delimiters, field_descriptors, extra_primitives
        )

    def parse_token(self, buffer: str) -> T:
        """
        Parse a buffer into a Token.

        Args:
            buffer: The string to parse into a Token. No newline splitting is done on the input.

        Returns:
            The buffer parsed into the underlying Token type.
        """
        return self.token_parser(buffer)

    def parse_sentence(self, buffer: str) -> S:
        """
        Parse a single sentence from the buffer.

        If there is more than one sentence in the buffer an error is thrown.

        Args:
            buffer: The string to parse for a single sentence.

        Returns:
            The single sentence that was parsed out of the string.
        """
        it = self.iter_from_string(buffer)
        sentence = next(it)

        stopped = False
        try:
            next(it)
        except StopIteration:
            stopped = True

        if not stopped:
            raise RuntimeError(
                "Expected only a single sentence from the buffer, but more than one was found."
            )

        return sentence

    def load_from_string(self, source: str) -> list[S]:
        """
        Parse a CoNLL formatted string into a list of sentences.

        Args:
            source: The CoNLL formatted string.

        Returns:
            A list of Sentence objects parsed from the source.

        Raises:
            ParseError: If there is an error parsing the input.
        """
        return list(self.iter_from_string(source))

    def load_from_file(self, filepath: PathLike) -> list[S]:
        """
        Parse a CoNLL file into a list of sentences.

        Assumes the file is UTF-8 encoded.

        Args:
            filepath: The path descriptor of the file to parse.

        Returns:
            A list of Sentence objects parsed from the file.

        Raises:
            IOError: If there is an error opening the given filename.
            ParseError: If there is an error parsing the input.
        """
        return list(self.iter_from_file(filepath))

    def load_from_resource(self, resource: io.TextIOBase) -> list[S]:
        """
        Parse a CoNLL resource into a list of sentences.

        Args:
            resource: The resource from which to read in the strings from. The resource must have
                universal newline reading enabled.

        Returns:
            A list of Sentence objects parsed from the resource.

        Raises:
            ParseError: If there is an error parsing the input.
        """
        return list(self.iter_from_resource(resource))

    def iter_from_string(self, source: str) -> Iterator[S]:
        """
        Iterate over the Sentences contained within the string.

        Args:
            source: The source string to extract the Sentence iterator from.

        Returns:
            The sentence iterator.

        Raises:
            ParseError: If there is an error parsing the input.
        """
        yield from self.iter_from_resource(io.StringIO(source))

    def iter_from_file(self, filepath: PathLike) -> Iterator[S]:
        """
        Iterate over the Sentence contained within the file.

        Assumes that the file is UTF-8 encoded.

        Args:
            filepath: The path descriptor of the file to parse.

        Returns:
            The sentence iterator.

        Raises:
            IOError: If there is an error opening the given filename.
            ParseError: If there is an error parsing the input.
        """
        with open(filepath, encoding="utf-8") as f:
            yield from self.iter_from_resource(f)

    def iter_from_resource(self, resource: io.TextIOBase) -> Iterator[S]:
        """
        Iterate over the Sentences contained within the resource.

        Args:
            resource: The resource from which to read in the strings from. The resource must have
                universal newline reading enabled.

        Returns:
            An iterator over the parsed Sentences within the resource.

        Raises:
            ParseError: If there is an error parsing the input.
        """
        sentence: S = self.sentence_schema()
        empty = True
        token_line_seen = False
        sentence_seen = False

        def step_next_sentence():
            nonlocal sentence, empty, token_line_seen, sentence_seen

            sentence.__finalize__()
            old = sentence

            sentence = self.sentence_schema()
            empty = True
            token_line_seen = False
            sentence_seen = True

            return old

        comment_len = len(self.comment_marker)

        i = 1
        while line := resource.readline():
            line_num = i
            i += 1
            if line.isspace():
                if not empty:
                    yield step_next_sentence()
                continue

            empty = False

            if line[0] == self.comment_marker:
                if token_line_seen:
                    raise ParseError(
                        f"Comment on line number {line_num} is coming after a non-comment line "
                        "has already been seen."
                    )

                equal_sep = line.find("=", 1)
                if equal_sep < 0:
                    key = _pair_down_whitespace(line, comment_len)
                    if key is not None:
                        sentence.__accept_meta__(key, None)
                else:
                    key = _pair_down_whitespace(line, comment_len, equal_sep) or ""
                    value = _pair_down_whitespace(line, equal_sep + 1) or ""
                    sentence.__accept_meta__(key, value)

            else:
                token_line_seen = True
                try:
                    token = self.token_parser(line)
                    sentence.__accept_token__(token)
                except ParseError as exc:
                    raise ParseError(
                        f"Error parsing token on line number {line_num} of the line source."
                    ) from exc

        if not empty or not sentence_seen:
            yield step_next_sentence()


class WriteFormat[T]:
    """
    A write-only interface for serializing CoNLL formatted data.

    This class wraps Serializer functionality and provides methods to serialize CoNLL data
    to various output formats including strings and IO resources. Use this when only
    serialization operations are needed.
    """

    def __init__(
        self,
        token_schema: type[T],
        comment_marker: str = "#",
        delimiter: str = "\t",
        field_descriptors: Optional[dict[str, Optional[FieldDescriptor]]] = None,
        extra_primitives: Optional[set[type]] = None,
    ) -> None:
        """
        Initialize the write format handler.

        Args:
            token_schema: The Token type to use for serialization.
            sentence_schema: The Sentence type to use for serialization.
            comment_marker: The prefix to use for comments or metadata. Defaults to '#'.
            delimiter: The delimiter between Token columns. Defaults to tab.
            field_descriptors: The descriptors for the fields on the schema as a mapping from the
                field name to the descriptor instance. For primitive types, use None as the
                descriptor. This takes precedence over anything on the type itself.
            extra_primitives: The set of types to consider as primitives (default construction and
                the str() operator are appropriate). This takes precedence over what is given on the
                tokenspec decorator.
        """
        self.serializer = _compile.token_serializer(
            token_schema, delimiter, field_descriptors, extra_primitives
        )
        self.comment_marker = comment_marker

    def serialize_token(self, token: T) -> str:
        """
        Serialize a token to a string representation.

        Args:
            token: The token to serialize.

        Returns:
            The serialized representation of the token.
        """
        return self.serializer(token)

    def serialize_sentence[S: AbstractSentence](self, sentence: S) -> str:
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

    def write_sentence[S: AbstractSentence](self, sentence: S, writable: io.TextIOBase) -> None:
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
            writable.write(self.serializer(token))
            writable.write("\n")

    def write_corpus[S: AbstractSentence](
        self, corpus: Iterator[S], writable: io.TextIOBase
    ) -> None:
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


class Format[T, S: AbstractSentence](ReadFormat[T, S], WriteFormat[T]):
    """
    A unified interface for both parsing and serializing CoNLL formatted data.

    This class combines the functionality of ReadFormat and WriteFormat through multiple
    inheritance, providing a complete read/write interface for CoNLL data. It maintains
    consistent formatting options (comment markers, delimiters) across both parsing and
    serialization operations.

    For typical use cases where both reading and writing are needed, this is the
    recommended class to use.
    """

    def __init__(
        self,
        token_schema: type[T],
        sentence_schema: type[S],
        comment_marker: str = "#",
        delimiter: str = "\t",
        collapse_delimiters: bool = False,
        field_descriptors: Optional[dict[str, Optional[FieldDescriptor]]] = None,
        extra_primitives: Optional[set[type]] = None,
    ) -> None:
        """
        Initialize the format handler with both read and write capabilities.

        Args:
            token_schema: The Token type to use for parsing and serialization.
            sentence_schema: The Sentence type to use for parsing and serialization.
            comment_marker: The character that marks the beginning of comments. Defaults to '#'.
            delimiter: The delimiter between the columns on a token line. Defaults to tab.
            collapse_delimiters: Flag if sequential delimiters denote an empty value or should be
                collapsed into one larger delimiter. Defaults to False.
            field_descriptors: The descriptors for the fields on the schema as a mapping from the
                field name to the descriptor instance. For primitive types, use None as the
                descriptor. This takes precedence over anything on the type itself.
            extra_primitives: The set of types to consider as primitives (default construction and
                the str() operator are appropriate). This takes precedence over what is given on the
                tokenspec decorator.
        """
        ReadFormat.__init__(
            self,
            token_schema,
            sentence_schema,
            comment_marker,
            delimiter,
            collapse_delimiters,
            field_descriptors,
            extra_primitives,
        )
        WriteFormat.__init__(
            self,
            token_schema,
            comment_marker,
            delimiter,
            field_descriptors,
            extra_primitives,
        )
