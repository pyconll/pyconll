"""
An internal module for common parsing logic, which is currently creating
Sentence objects from an iterator that returns CoNLL source lines. This logic
can then be used in Conll or in pyconll.load.
"""

from pyconll.unit import Sentence


def _determine_sentence_id(sentence, new_id, id_name, old_id):
    """
    Determine the appropriate id for this sentence.

    Ids here means doc id or par id.

    Args:
        sentence: The sentence whose ids to check.
        new_id: The key that the id can come up as without the id key word.
        id_name: The id in the comments to modify. One of 'newpar id', or
            'newdoc id'.
        old_id: The id of the previous sentence.

    Returns:
        The value of the id of the sentence.
    """
    if sentence.meta_present(id_name):
        return sentence.meta_value(id_name)

    if sentence.meta_present(new_id):
        return None

    return old_id


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


def _create_configured_sentence(sent_lines, start_line, cur_par_id,
                                cur_doc_id):
    """
    Creates a Sentence with configured line bounds and paragraph and doc ids.

    Args:
        sent_lines: An iterable of the lines that make up the Sentence source.
        start_line: The line number for the start of the lines.
        cur_par_id: The current, in context, paragraph id.
        cur_doc_id: The current, in context, document id.

    Returns:
        The created Sentence with configured paragraph and document ids.

    Raises:
        ParseError: If the sentence source is not valid.
    """
    sentence = _create_sentence(sent_lines, start_line)

    cur_par_id = _determine_sentence_id(sentence, Sentence.NEWPAR_KEY,
                                        Sentence.NEWPAR_ID_KEY, cur_par_id)
    sentence._set_par_id(cur_par_id)
    cur_doc_id = _determine_sentence_id(sentence, Sentence.NEWDOC_KEY,
                                        Sentence.NEWDOC_ID_KEY, cur_doc_id)
    sentence._set_doc_id(cur_doc_id)

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
    cur_par_id = None
    cur_doc_id = None

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
            sentence = _create_configured_sentence(sent_lines, last_start,
                                                   cur_par_id, cur_doc_id)
            sent_lines.clear()

            cur_par_id = sentence.par_id
            cur_doc_id = sentence.doc_id

            yield sentence

    if sent_lines:
        sentence = _create_configured_sentence(sent_lines, last_start,
                                               cur_par_id, cur_doc_id)
        yield sentence
