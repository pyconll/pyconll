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
    elif sentence.meta_present(new_id):
        return None
    else:
        return old_id


def _create_sentence(sent_lines, start, end):
    """
    Creates a Sentence object given the current state of the source iteration.

    Args:
        sent_lines: An iterable of the lines that make up the source.
        start: The line number for the start of the Sentence.
        end: The line number for the end of the Sentence.

    Returns:
        The created Sentence.

    Raises:
        ValueError: If the sentence source is not valid.
    """
    sent_source = '\n'.join(sent_lines)
    sentence = Sentence(
        sent_source, _start_line_number=start, _end_line_number=end)
    sent_lines.clear()

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
            sentence = _create_sentence(sent_lines, last_start, i)

            cur_par_id = _determine_sentence_id(sentence, Sentence.NEWPAR_KEY,
                                                Sentence.NEWPAR_ID_KEY,
                                                cur_par_id)
            sentence._set_par_id(cur_par_id)
            cur_doc_id = _determine_sentence_id(sentence, Sentence.NEWDOC_KEY,
                                                Sentence.NEWDOC_ID_KEY,
                                                cur_doc_id)
            sentence._set_doc_id(cur_doc_id)

            yield sentence

    if sent_lines:
        sentence = _create_sentence(sent_lines, last_start, i)

        cur_par_id = _determine_sentence_id(sentence, Sentence.NEWPAR_KEY,
                                            Sentence.NEWPAR_ID_KEY, cur_par_id)
        sentence._set_par_id(cur_par_id)
        cur_doc_id = _determine_sentence_id(sentence, Sentence.NEWDOC_KEY,
                                            Sentence.NEWDOC_ID_KEY, cur_doc_id)
        sentence._set_doc_id(cur_doc_id)

        yield sentence
