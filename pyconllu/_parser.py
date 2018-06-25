from pyconllu.unit import Sentence


def iter_sentences(lines_it):
    """
    Iterate over the constructed sentences in the given lines.

    This method correctly takes into account newpar and newdoc comments as well.

    Args:
    lines_it: An iterator over the lines to parse.

    Returns:
    An iterator over the constructed Sentence objects found in the source.
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
            cur_par_id = _assign_sentence_ids(sentence, 'newpar', '_par_id',
                                              cur_par_id)
            cur_doc_id = _assign_sentence_ids(sentence, 'newdoc', '_doc_id',
                                              cur_doc_id)

            yield sentence

    if sent_lines:
        sentence = _create_sentence(sent_lines, last_start, i)
        cur_par_id = _assign_sentence_ids(sentence, 'newpar', '_par_id',
                                          cur_par_id)
        cur_doc_id = _assign_sentence_ids(sentence, 'newdoc', '_doc_id',
                                          cur_doc_id)

        yield sentence


def _assign_sentence_ids(sentence, meta_key, id_name, old_id):
    """
    Assign the appropriate id to the sentence and return the current id.

    Ids here means doc id or par id.

    Args:
    sentence: The sentence whose ids to check.
    meta_key: The key that the id can come up as without the id key word.
    id_name: The id to modify. One of '_par_id', or '_doc_id'.
    old_id: The id of the previous sentence.

    Returns:
    The value of the id of the sentence.
    """
    if getattr(sentence, id_name) is not None or \
        sentence.meta_present(meta_key):
        return getattr(sentence, id_name)
    else:
        setattr(sentence, id_name, old_id)
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
    """
    sent_source = '\n'.join(sent_lines)
    sentence = Sentence(
        sent_source, _start_line_number=start, _end_line_number=end)
    sent_lines.clear()

    return sentence
