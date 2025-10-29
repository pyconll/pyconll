"""
An internal module for common parsing logic, which is currently creating
Sentence objects from an iterator that returns CoNLL source lines. This logic
can then be used in the Conll class or in pyconll.load.
"""

from collections import OrderedDict
import string
from typing import Callable, ClassVar, Iterable, Iterator, Optional

from pyconll.exception import ParseError
from pyconll.schema import compile_token_parser
from pyconll.unit.sentence import Sentence
from pyconll.unit.token import Token


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


class _ParsingData:
    COMMENT_MARKER: ClassVar[str] = "#"
    PARSER_CACHE: ClassVar[dict[type, Callable[[str], Token]]] = {}


def iter_sentences(lines_it: Iterable[str]) -> Iterator[Sentence]:
    """
    Iterate over the constructed sentences in the given lines.

    This method correctly takes into account newpar and newdoc comments as well.

    Args:
        lines_it: An iterator over the lines to parse.

    Yields:
        An iterator over the constructed Sentence objects found in the source.

    Raises:
        ValueError: If there is an error constructing the Sentence.
    """
    try:
        token_parser = _ParsingData.PARSER_CACHE[Token]
    except KeyError:
        token_parser = _ParsingData.PARSER_CACHE[Token] = compile_token_parser(Token)

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

    for i, line in enumerate(lines_it):
        if line in ("\n", "\r\n", ""):
            if not empty:
                yield step_next_sentence()
            continue

        empty = False
        comment_len = len(_ParsingData.COMMENT_MARKER)

        if line[0] == _ParsingData.COMMENT_MARKER:
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
                token = token_parser(line)
                tokens.append(token)
                if token.id is not None:
                    ids_to_indexes[token.id] = len(tokens) - 1
            except ParseError as exc:
                raise ParseError(
                    f"Error parsing token on line number {i} of the line source."
                ) from exc

    if not empty or not sentence_seen:
        yield step_next_sentence()
