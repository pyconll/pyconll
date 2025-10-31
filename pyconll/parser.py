"""
An internal module for common parsing logic, which is currently creating
Sentence objects from an iterator that returns CoNLL source lines. This logic
can then be used in the Conll class or in pyconll.load.
"""

import io
import os
from collections import OrderedDict
import string
from typing import Callable, Iterator, Optional

from pyconll.exception import ParseError
from pyconll.schema import compile_token_parser
from pyconll.unit.sentence import Sentence
from pyconll.unit.token import Token

PathLike = str | bytes | os.PathLike


class Parser:
    """
    A parser for CoNLL-U formatted data.

    The parser maintains state including the comment marker and token parser, and provides methods
    to parse from various sources. In all cases, the parser will handle windows or unix newlines.
    """

    def __init__(self, token_type: type[Token] = Token, comment_marker: str = "#") -> None:
        """
        Initialize the parser.

        Args:
            token_type: The Token type to use for parsing. Defaults to Token.
            comment_marker: The string that marks the beginning of comments.
                Defaults to '#'.
        """
        self.comment_marker = comment_marker
        self.token_parser: Callable[[str], Token] = compile_token_parser(token_type)

    def load_from_string(self, source: str) -> list[Sentence]:
        """
        Parse a CoNLL-U formatted string into a list of sentences.

        Args:
            source: The CoNLL-U formatted string.

        Returns:
            A list of Sentence objects parsed from the source.

        Raises:
            ParseError: If there is an error parsing the input.
        """
        return list(self.iter_from_string(source))

    def load_from_file(self, filepath: PathLike) -> list[Sentence]:
        """
        Parse a CoNLL-U file into a list of sentences.

        Args:
            filepath: The path descriptor of the file to parse.

        Returns:
            A list of Sentence objects parsed from the file.

        Raises:
            IOError: If there is an error opening the given filename.
            ParseError: If there is an error parsing the input.
        """
        return list(self.iter_from_file(filepath))

    def load_from_resource(self, resource: io.TextIOBase) -> list[Sentence]:
        """
        Parse a CoNLL-U resource into a list of sentences.

        Args:
            resource: The resource from which to read in the strings from. The resource must have
                universal newline reading enabled.

        Returns:
            A list of Sentence objects parsed from the resource.

        Raises:
            ParseError: If there is an error parsing the input.
        """
        return list(self.iter_from_resource(resource))

    def iter_from_string(self, source: str) -> Iterator[Sentence]:
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

    def iter_from_file(self, filepath: PathLike) -> Iterator[Sentence]:
        """
        Iterate over the Sentence contained within the file.

        Assumes that the file is utf-8 encoded.

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

    def iter_from_resource(self, resource: io.TextIOBase) -> Iterator[Sentence]:
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
        meta: OrderedDict[str, Optional[str]] = OrderedDict()
        tokens: list[Token] = []
        ids_to_indexes: dict[str, int] = {}
        empty = True
        token_line_seen = False
        sentence_seen = False

        def step_next_sentence():
            nonlocal meta, tokens, ids_to_indexes, empty, token_line_seen, sentence_seen

            sentence = Sentence(meta, tokens, ids_to_indexes)

            meta = OrderedDict()
            tokens = []
            ids_to_indexes = {}
            empty = True
            token_line_seen = False
            sentence_seen = True

            return sentence

        comment_len = len(self.comment_marker)

        i = 1
        while line := resource.readline():
            line_num = i
            i += 1
            if line in ("\n", "\r\n", ""):
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
                        meta[key] = None
                else:
                    key = _pair_down_whitespace(line, comment_len, equal_sep) or ""
                    value = _pair_down_whitespace(line, equal_sep + 1) or ""

                    meta[key] = value

            else:
                token_line_seen = True
                try:
                    token = self.token_parser(line)
                    tokens.append(token)
                    if token.id is not None:
                        ids_to_indexes[token.id] = len(tokens) - 1
                except ParseError as exc:
                    raise ParseError(
                        f"Error parsing token on line number {line_num} of the line source."
                    ) from exc

        if not empty or not sentence_seen:
            yield step_next_sentence()


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
