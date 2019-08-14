"""
A set of utilities for dealing with pyconll defined types. This is simply a
collection of functions.
"""

import functools
import itertools
import math


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
            insensitive lowercase comparison.

    Returns:
        An iterator of tuples over the ngrams in the Conll object. The first
        element is the sentence, the second element is the numeric token index,
        and the last element is the actual list of tokens references from the
        sentence. This list does not include any multiword token that were
        skipped over.
    """
    matched_tokens = []

    for sentence in conll:
        i = 0

        while i <= len(sentence) - len(ngram):
            token = sentence[i]

            cased_form, cased_ngram_start = _get_cased(case_sensitive,
                                                       token.form, ngram[0])

            if cased_form == cased_ngram_start and not token.is_multiword():
                matches = True
                matched_tokens.append(token)
                cur_idx = i

                for ngram_token in itertools.islice(ngram, 1, None):
                    cur_idx += 1
                    new_token = sentence[cur_idx]

                    if new_token.is_multiword():
                        cur_idx += 1
                        new_token = sentence[cur_idx]

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


def find_nonprojective_deps(sentence):
    """
    Find the nonprojective dependency pairs in the provided sentence.

    Args:
        sentence: The sentence to check for nonprojective dependency pairs.

    Returns:
        An iterable of pairs which represent the children of a nonprojective
        dependency pair.
    """
    non_root_tokens = filter(lambda token: token.head != '0', sentence)
    deps = list(map(_token_to_dep_tuple, non_root_tokens))

    sorted_deps = sorted(deps, key=_DependencyComparer)
    non_projective_deps = []

    openings = [-math.inf]
    closings = [math.inf]
    direcs = ['']

    for dep in sorted_deps:

        cur_opening = openings[-1]
        cur_closing = closings[-1]
        cur_direc = direcs[-1]

        left_index, right_index, direc = dep

        starts_outside = left_index >= cur_closing
        if starts_outside:
            while left_index >= closings[-1]:
                openings.pop()
                closings.pop()
                direcs.pop()

        within_range = cur_opening < right_index <= cur_closing
        if not within_range:
            for i in range(len(openings) - 1, -1, -1):
                o = openings[i]
                c = closings[i]
                d = direcs[i]
                if right_index > c:
                    dep_child_idx = dep[1] if dep[2] == 'l' else dep[0]
                    base_child_idx = c if d == 'l' else o
                    non_projective_deps.append((dep_child_idx, base_child_idx))
                else:
                    break

        if starts_outside or within_range:
            openings.append(left_index)
            closings.append(right_index)
            direcs.append(direc)

    child_tokens = list(map(lambda dep: tuple(map(lambda idx: sentence[str(idx)], dep)), non_projective_deps))
    return child_tokens


def _dep_to_token_pair(sentence, dep):
    """
    """
    head_idx = dep[0] if dep[2] == 'l' else dep[1]
    child_idx = dep[1] if dep[2] == 'l' else dep[0]

    return (sentence[head_idx], sentence[child_idx])


# TODO
@functools.total_ordering
class _DependencyComparer:
    """
    """

    def __init__(self, dep):
        """
        """
        self._l, self._r, _ = dep

    def __eq__(self, other):
        """
        """
        return self._l == other._l and self._r == other._r

    def __ne__(self, other):
        """
        """
        return not (self == other)

    def __lt__(self, other):
        """
        """
        return self._l < other._l or (self._l == other._l
                                      and self._r > other._r)


def _token_to_dep_tuple(token):
    """
    Creates a tuple of primitives to represent the dependency on a token.

    Args:
        token: The token to convert to a tupled dependency representation.

    Returns:
        A triplet where the first element is the minimum of the token id and
        governor id, the second is the maximum, and the third is the direction
        of the dependency.
    """
    id_i = int(token.id)
    head_i = int(token.head)
    if id_i < head_i:
        return (id_i, head_i, 'r')
    else:
        return (head_i, id_i, 'l')


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
