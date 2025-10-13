"""
An internal module for common parsing logic, which is currently creating
Sentence objects from an iterator that returns CoNLL source lines. This logic
can then be used in the Conll class or in pyconll.load.
"""

from typing import Iterable, Iterator

from pyconll.exception import ParseError
from pyconll.unit.sentence import Sentence


def _create_sentence(sent_lines: Iterable[str], line_num: int) -> Sentence:
    """
    Creates a Sentence object given the current state of the source iteration.

    Args:
        sent_lines: An iterable of the lines that make up the source.
        line_num: The current line number the sentence starts at, for logging
            purposes.

    Returns:
        The created Sentence.

    Raises:
        ParseError: If the sentence source is not valid.
    """
    sent_source = "\n".join(sent_lines)
    try:
        sentence = Sentence(sent_source)
    except ParseError as err:
        raise ParseError(f"Failed to create sentence at line {line_num}") from err

    return sentence


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
