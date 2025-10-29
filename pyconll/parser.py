"""
An internal module for common parsing logic, which is currently creating
Sentence objects from an iterator that returns CoNLL source lines. This logic
can then be used in the Conll class or in pyconll.load.
"""

import os
from collections import OrderedDict
import string
from typing import Callable, Iterable, Iterator, Optional

from pyconll.exception import ParseError
from pyconll.schema import compile_token_parser
from pyconll.unit.sentence import Sentence
from pyconll.unit.token import Token

PathLike = str | bytes | os.PathLike


class Parser:
    """
    A parser for CoNLL-U formatted data.

    The parser maintains state including the comment marker and token parser,
    and provides methods to parse from various sources.
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

    def load_from_file(self, file_descriptor: PathLike) -> list[Sentence]:
        """
        Parse a CoNLL-U file into a list of sentences.

        Args:
            file_descriptor: The file to load the CoNLL-U data from. This can be a
                filepath as a Path object, or string, or a file descriptor.

        Returns:
            A list of Sentence objects parsed from the file.

        Raises:
            IOError: If there is an error opening the given filename.
            ParseError: If there is an error parsing the input.
        """
        return list(self.iter_from_file(file_descriptor))

    def load_from_resource(self, resource: Iterable[str]) -> list[Sentence]:
        """
        Parse a CoNLL-U resource into a list of sentences.

        Args:
            resource: The generic string resource. Each string from the resource is
                assumed to be a line in a CoNLL-U formatted resource.

        Returns:
            A list of Sentence objects parsed from the resource.

        Raises:
            ParseError: If there is an error parsing the input.
        """
        return list(self.iter_from_resource(resource))

    def iter_from_string(self, source: str) -> Iterator[Sentence]:
        """ """
        # TODO: Do something better regarding this not duplicating the memory requirement
        # TODO: Think about what is expected for new-line handling here wrt to flexibility
        #       and standards as well (default should be permissive but if someone wants something
        #       different it is possible to set.)
        lines = source.splitlines()
        yield from self.iter_from_resource(lines)

    def iter_from_file(self, file_descriptor: PathLike) -> Iterator[Sentence]:
        """ """
        with open(file_descriptor, encoding="utf-8") as f:
            yield from self.iter_from_resource(f)

    def iter_from_resource(self, resource: Iterable[str]) -> Iterator[Sentence]:
        """ """
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

        for i, line in enumerate(resource):
            if line in ("\n", "\r\n", ""):
                if not empty:
                    yield step_next_sentence()
                continue

            empty = False
            comment_len = len(self.comment_marker)

            if line[0] == self.comment_marker:
                if token_line_seen:
                    raise ParseError(
                        f"Comment on line number {i} is coming after a non-comment line "
                        "has already been seen."
                    )

                equal_sep = line.find("=")
                if equal_sep < 0:
                    key = _pair_down_whitespace(line, comment_len)
                    value = None
                else:
                    key = _pair_down_whitespace(line, comment_len, equal_sep)
                    value = _pair_down_whitespace(line, equal_sep + 1)

                if key is None:
                    raise ParseError(f"Comment on line number {i} has no key value.")

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
                        f"Error parsing token on line number {i} of the line source."
                    ) from exc

        if not empty or not sentence_seen:
            yield step_next_sentence()


def _pair_down_whitespace(
    line: str, start_idx: int, end_idx: Optional[int] = None
) -> Optional[str]:
    while start_idx < len(line) and line[start_idx] in string.whitespace:
        start_idx += 1

    if start_idx == len(line):
        return None

    end_idx = len(line) if end_idx is None else end_idx
    while (end_idx - 1) > start_idx and line[end_idx - 1] in string.whitespace:
        end_idx -= 1

    return line[start_idx:end_idx]
