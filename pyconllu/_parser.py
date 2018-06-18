from pyconllu.unit import Sentence


def iter_sentences(lines_it):
    """
    Iterate over the constructed sentences in the given lines.

    Args:
    lines_it: An iterator over the lines to parse.

    Returns:
    An iterator over the constructed Sentence objects found in the source.
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
            yield _create_sentence(sent_lines, last_start, i)

    if sent_lines:
        yield _create_sentence(sent_lines, last_start, i)


def _create_sentence(sent_lines, start, end):
    """
    Creates a Sentence object given the current state of the source iteration.

    Args:
    sent_lines: An iterable of the lines that make up the source.
    start: The line number for the start of the Sentence.
    end: The line number for the end of the Sentence.

    Returns:
    The create Sentence.
    """
    sent_source = '\n'.join(sent_lines)
    sentence = Sentence(
        sent_source, _start_line_number=start, _end_line_number=end)
    sent_lines.clear()

    return sentence
