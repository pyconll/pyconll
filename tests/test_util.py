import operator

import pytest

from pyconll.util import find_ngrams
from pyconll import load_from_file
from tests.util import fixture_location


def test_ngram_standard():
    """
    Test if the find_ngram method works for standard situations.
    """
    c = load_from_file(fixture_location('basic.conll'))

    s, i = next(find_ngrams(c, 'un film sur la'.split()))
    assert s.id == 'fr-ud-dev_00001'
    assert i == 2


def test_ngram_multiple_per_sentence():
    """
    Test that all ngrams are found when there are multiple in the same sentence.
    """
    c = load_from_file(fixture_location('long.conll'))
    results = list(find_ngrams(c, 'telle ou telle'.split()))

    actual_ids = list(map(lambda res: res[0].id, results))
    actual_indices = list(map(operator.itemgetter(1), results))

    expected_ids = ['fr-ud-test_00008', 'fr-ud-test_00008']
    expected_indices = [21, 26]

    assert actual_ids == expected_ids
    assert actual_indices == expected_indices


def test_ngram_none():
    """
    Test that no ngram is identified when no exist
    """
    c = load_from_file(fixture_location('long.conll'))
    it = find_ngrams(c, 'cabinet'.split())

    with pytest.raises(StopIteration):
        next(it)


def test_ngram_first_word_match():
    """
    Test that a first word match is not enough to match.
    """
    c = load_from_file(fixture_location('long.conll'))
    it = find_ngrams(c, 'un cabinet'.split())

    with pytest.raises(StopIteration):
        next(it)
