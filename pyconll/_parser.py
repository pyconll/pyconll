"""
An internal module for common parsing logic, which is currently creating
Sentence objects from an iterator that returns CoNLL source lines. This logic
can then be used in the Conll class or in pyconll.load.
"""

from collections import OrderedDict
import re
from typing import Callable, Iterable, Iterator, Optional

from pyconll.exception import ParseError
from pyconll.unit.sentence import Sentence
from pyconll.unit.token import Token


def _create_sentence(token_parser: Callable[[str], Token], sent_lines: Iterable[str], line_num: int) -> Sentence:
    """
    Creates a Sentence object given the current state of the source iteration.

    Args:
        token_parser: Parser from a Token line into the actual in memory representation.
        sent_lines: An iterable of the lines that make up the source.
        line_num: The current line number the sentence starts at, for logging
            purposes.

    Returns:
        The created Sentence.

    Raises:
        ParseError: If the sentence source is not valid.
    """
    meta: OrderedDict[str, Optional[str]] = OrderedDict()
    tokens: list[Token] = []

    for i, line in enumerate(sent_lines):
        if line:
            if line[0] == Sentence.COMMENT_MARKER:
                kv_match = re.match(Sentence.KEY_VALUE_COMMENT_PATTERN, line)

                if kv_match:
                    k = kv_match.group(1)
                    v = kv_match.group(2)
                    meta[k] = v
                else:
                    singleton_match = re.match(Sentence.SINGLETON_COMMENT_PATTERN, line)
                    if singleton_match:
                        k = singleton_match.group(1)
                        meta[k] = None
            else:
                try:
                    token = token_parser(line)
                    tokens.append(token)
                except ParseError as exc:
                    raise ParseError(
                        f"Error creating token on line {line_num + i} for the current sentence"
                    ) from exc

    return Sentence(meta, tokens)


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
    sent_lines = []
    last_empty_line = -1
    for i, line in enumerate(lines_it):
        line = line.strip()

        # Collect all lines until there is a blank line. Then all the
        # collected lines were between blank lines and are a sentence.
        if line:
            sent_lines.append(line)
        else:
            if sent_lines:
                sentence = _create_sentence(sent_lines, last_empty_line + 2)
                sent_lines.clear()
                yield sentence

            last_empty_line = i

    if sent_lines:
        sentence = _create_sentence(sent_lines, last_empty_line)
        yield sentence
