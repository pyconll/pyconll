"""
An internal module for common parsing logic, which is currently creating
Sentence objects from an iterator that returns CoNLL source lines. This logic
can then be used in the Conll class or in pyconll.load.
"""

from pyconll.unit import Sentence


def _create_sentence(sent_lines, start):
    """
    Creates a Sentence object given the current state of the source iteration.

    Args:
        sent_lines: An iterable of the lines that make up the source.
        start: The line number for the start of the Sentence.

    Returns:
        The created Sentence.

    Raises:
        ParseError: If the sentence source is not valid.
    """
    sent_source = '\n'.join(sent_lines)
    sentence = Sentence(sent_source, _start_line_number=start)

    return sentence


def iter_sentences(lines_it):
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
    last_start = -1

    sent_lines = []
    for i, line in enumerate(lines_it):
        line = line.strip()

        # Collect all lines until there is a blank line. Then all the
        # collected lines were between blank lines and are a sentence.
        if line:
            if not sent_lines:
                last_start = i + 1

            sent_lines.append(line)
        elif sent_lines:
            sentence = _create_sentence(sent_lines, last_start)
            sent_lines.clear()

            yield sentence

    if sent_lines:
        sentence = _create_sentence(sent_lines, last_start)
        yield sentence
