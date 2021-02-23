"""
A set of utilities for dealing with pyconll defined types. This is simply a
collection of functions.
"""

import functools
import itertools
from typing import Iterable, Iterator, Sequence, List, Tuple

from pyconll.unit.sentence import Sentence
from pyconll.unit.token import Token


def find_ngrams(
    conll: Iterable[Sentence],
    ngram: Sequence[str],
    case_sensitive: bool = True
) -> Iterator[Tuple[Sentence, int, List[Token]]]:
    """
    Find the occurrences of the ngram in the provided Conll collection.

    This method returns every sentence along with the token position in the
    sentence that starts the ngram. The matching algorithm does not currently
    account for multiword tokens, so "don't" should be separated into "do" and
    "not" in the input.

    Args:
        conll: The corpus in which to search for the ngram across the sentences.
        ngram: The ngram to search for. An iterator of the lemmas.
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
                    else:
                        matched_tokens.append(new_token)

                if matches:
                    yield (sentence, i, matched_tokens)
                    matched_tokens = []

            i += 1


def find_nonprojective_deps(sentence: Sentence) -> List[Tuple[Token, Token]]:
    """
    Find the nonprojective dependency pairs in the provided sentence.

    Dependencies are provided as a list of ordered pairs. Each ordered pair
    represents a non-projective dependency pair. Each element in the ordered
    pair is a token, that makes a dependency with its governor. So each token
    is the base of its dependency, and the two tokens' dependencies cross in
    a non projective way.

    Args:
        sentence: The sentence to check for nonprojective dependency pairs.

    Returns:
        An list of pairs which represent the children of a nonprojective
        dependency pair.
    """
    deps = _transform_tokens_to_sorted_dependency_arcs(sentence)
    non_projective_deps: List[Tuple[int, int]] = []

    openings = [-1]
    closings = [len(sentence)]
    direcs = ['']

    for dep in deps:
        cur_opening = openings[-1]
        cur_closing = closings[-1]

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

    child_tokens = list(
        map(lambda dep: (sentence[dep[0]], sentence[dep[1]]),
            non_projective_deps))
    return child_tokens


def _transform_tokens_to_sorted_dependency_arcs(sentence):
    """
    Transforms a given sentence or set of tokens into dependency arcs.

    These dependency arcs are tuples which consist of a head id, a token id and
    head direction. These dependencies are sorted to facilitate non-projectivity
    detection.

    Args:
        sentence: The tokens to transform to dependency arcs.

    Returns:
        The sorted list of dependency arcs extracted from the sentence.
    """
    # Create a string token id to numeric index map for the sentence.
    ids_to_idxs = {token.id: i for i, token in enumerate(sentence)}

    dependency_tokens = filter(
        lambda token: token.head != '0' and not token.is_multiword(), sentence)
    deps = sorted(map(lambda token: _token_to_dep_tuple(token, ids_to_idxs),
                      dependency_tokens),
                  key=_DependencyComparer)

    return deps


@functools.total_ordering
class _DependencyComparer:
    """
    Wrapper to compare dependency arcs.
    """
    def __init__(self, dep):
        """
        Creates the wrapper for this dependency.

        Args:
            dep: The dependency to wrap.
        """
        self._l, self._r, _ = dep

    def __eq__(self, other):
        """
        Checks that this dependency has the same indices as another.

        Args:
            other: The other wrapped dependency to compare against.
        """
        return self._l == other._l and self._r == other._r

    def __ne__(self, other):
        """
        Checks that this dependency has different indices as another.

        Args:
            other: Another wrapped dependency to compare against.
        """
        return not self == other

    def __lt__(self, other):
        """
        Checks that this dependency is less than another.

        This comparison is done by first checking the smaller of the two
        indices. The second indices are compared if the first are equal and this
        dependency will be smaller if its second index is larger.

        Args:
            other: Another wrapped dependency to compare against.
        """
        return self._l < other._l or (self._l == other._l
                                      and self._r > other._r)


def _token_to_dep_tuple(token, id_map):
    """
    Creates a tuple of primitives to represent the dependency on a token.

    Args:
        token: The token to convert to a tupled dependency representation.
        id_map: A mapping from string token ids to indices.

    Returns:
        A triplet where the first element is the minimum of the token id and
        governor id, the second is the maximum, and the third is the direction
        of the dependency.
    """
    token_idx = id_map[token.id]
    head_idx = id_map[token.head]
    if token_idx < head_idx:
        return (token_idx, head_idx, 'r')

    return (head_idx, token_idx, 'l')


def _get_cased(case_sensitive, *args):
    """
    Get the cased versions of the provided strings if applicable.

    Args:
        case_sensitive: If False, then returns lowercase versions of all
            strings.
        args: The strings to get appropriately cased versions of.

    Returns:
        An iterable of case converted strings as necessary.
    """
    if not case_sensitive:
        args = list(map(str.lower, args))
    return args
