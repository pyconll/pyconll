"""
The main parser component. For more common CoNLL-U parsing, the pyconll.load_* and pyconll.iter_*
methods may be more succinct but for more general scenarios, this can be used as necessary.
"""

import io
import os
from collections import OrderedDict
import string
from typing import Iterator, Optional

from pyconll.exception import ParseError
from pyconll.schema import TokenSchema, _compile_token_parser
from pyconll.sentence import Sentence

PathLike = str | bytes | os.PathLike


class Parser[T: TokenSchema]:
    """
    A parser for CoNLL formatted data.

    The parser maintains state including the comment marker, delimiter, and the compiled parser,
    and provides methods to parse from various sources. In all cases, the parser will handle both
    windows or unix newlines where the text resource is not explicitly provided.
    """

    def __init__(
        self, token_type: type[T], comment_marker: str = "#", delimiter: str = "\t"
    ) -> None:
        """
        Initialize the parser.

        Args:
            token_type: The Token type to use for parsing.
            comment_marker: The string that marks the beginning of comments. Defaults to '#'.
            delimiter: The delimiter between the columns on a token line.
        """
        self.comment_marker = comment_marker
        self.delimiter = delimiter
        self.token_parser = _compile_token_parser(token_type)

    def load_from_string(self, source: str) -> list[Sentence[T]]:
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

    def load_from_file(self, filepath: PathLike) -> list[Sentence[T]]:
        """
        Parse a CoNLL-U file into a list of sentences.

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

    def load_from_resource(self, resource: io.TextIOBase) -> list[Sentence[T]]:
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

    def iter_from_string(self, source: str) -> Iterator[Sentence[T]]:
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

    def iter_from_file(self, filepath: PathLike) -> Iterator[Sentence[T]]:
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

    def iter_from_resource(self, resource: io.TextIOBase) -> Iterator[Sentence[T]]:
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
        tokens: list[T] = []
        empty = True
        token_line_seen = False
        sentence_seen = False

        def step_next_sentence() -> Sentence[T]:
            nonlocal meta, tokens, empty, token_line_seen, sentence_seen

            sentence = Sentence[T](meta, tokens)

            meta = OrderedDict()
            tokens = []
            empty = True
            token_line_seen = False
            sentence_seen = True

            return sentence

        comment_len = len(self.comment_marker)

        i = 1
        while line := resource.readline():
            line_num = i
            i += 1
            if line.isspace() or line == "":
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
                    token = self.token_parser(line, self.delimiter)
                    tokens.append(token)
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
