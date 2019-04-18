"""
A set of utilities for dealing with pyconll defined types. This is simply a
collection of functions.
"""

import itertools


def find_ngrams(conll, ngram, case_sensitive=True):
    """
    Find the occurences of the ngram in the provided Conll collection.

    This method returns every sentence along with the token position in the
    sentence that starts the ngram. The matching algorithm does not currently
    account for multiword tokens, so "don't" should be separated into "do" and
    "not" in the input.

    Args:
        sentence: The sentence in which to search for the ngram.
        ngram: The ngram to search for. A random access iterator.
        case_sensitive: Flag to indicate if the ngram search should be case
            sensitive. The case insensitive comparison currently is locale
            insensitive as the default behavior of python.

    Returns:
        An iterator of tuples over the ngrams in the Conll object. The first
        element is the sentence, the second element is the numeric token index,
        and the last element is the actual list of tokens references from the
        sentence.
    """
    for sentence in conll:
        i = 0

        while i < len(sentence):
            token = sentence[i]

            cased_form, cased_ngram_start = _get_cased(case_sensitive,
                                                       token.form, ngram[0])

            if cased_form == cased_ngram_start and not token.is_multiword():
                matches = True
                matched_tokens = [token]
                multiword_token_offset = 0

                for j, ngram_token in enumerate(
                        itertools.islice(ngram, 1, None)):
                    new_token = sentence[i + j + multiword_token_offset + 1]
                    if new_token.is_multiword():
                        multiword_token_offset += 1
                        new_token = sentence[i + j + multiword_token_offset +
                                             1]

                    cased_new_token_form, cased_ngram_token = _get_cased(
                        case_sensitive, new_token.form, ngram_token)
                    if cased_new_token_form != cased_ngram_token:
                        matches = False
                        matched_tokens.clear()
                        break
                    else:
                        matched_tokens.append(new_token)

                if matches:
                    yield (sentence, i, matched_tokens)
                    matched_tokens = []

            i += 1


def _get_cased(case_sensitive, *args):
    """
    Get the cased versions of the provided strings if applicable.

    Args:
        case_sensitive: If False, then returns lowercase versions of all
            strings.
        args: The strings to get appropriately cased versions of.

    Returns:
        An iterable  of case converted strings as necessary.
    """
    if not case_sensitive:
        args = list(map(str.lower, args))
    return args
