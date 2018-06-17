from pyconllu.unit import Sentence


def iter_sentences(lines_it):
    """
    Iterate over the constructed sentences in the given lines.

    Args:
    lines_it: An iterator over the lines to parse.

    Returns:
    An iterator over the constructed Sentence objects found in the source.
    """
    sent_lines = []
    for line in lines_it:
        line = line.strip()

        # Collect all lines until there is a blank line. Then all the
        # collected lines were between blank lines and are a sentence.
        if line:
            sent_lines.append(line)
        elif sent_lines:
            sent_source = '\n'.join(sent_lines)
            sentence = Sentence(sent_source)
            sent_lines.clear()

            yield sentence

    if sent_lines:
        sent_source = '\n'.join(sent_lines)
        sentence = Sentence(sent_source)
        sent_lines.clear()

        yield sentence
