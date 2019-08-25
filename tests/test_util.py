import operator

import pytest

from pyconll.util import find_ngrams, find_nonprojective_deps
from pyconll import load_from_file
from tests.util import fixture_location


def test_ngram_standard():
    """
    Test if the find_ngram method works for standard situations.
    """
    c = load_from_file(fixture_location('basic.conll'))

    s, i, _ = next(find_ngrams(c, 'un film sur la'.split()))

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
    Test that no ngram is identified when none exist
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


def test_ngram_multiword_split():
    """
    Test that ngram searches still work when they go over a multiword token.
    """
    c = load_from_file(fixture_location('long.conll'))

    it = find_ngrams(c, 'de " décentrement de le Sujet "'.split())
    s, i, tokens = next(it)

    actual_token_ids = list(map(lambda token: token.id, tokens))
    expected_token_ids = ['9', '10', '11', '12', '13', '14', '15']

    assert s.id == 'fr-ud-test_00002'
    assert i == 8
    assert actual_token_ids == expected_token_ids

    with pytest.raises(StopIteration):
        next(it)


def test_ngram_multiple_multiword_splits():
    """
    Test that ngram searches work when they there is more than one multiword token.
    """
    c = load_from_file(fixture_location('long.conll'))

    it = find_ngrams(
        c, 'civile de le territoire non autonome de le Sahara'.split())
    s, i, tokens = next(it)

    actual_token_ids = list(map(lambda token: token.id, tokens))
    expected_token_ids = ['10', '11', '12', '13', '14', '15', '16', '17', '18']

    assert s.id == 'fr-ud-test_00003'
    assert i == 9
    assert actual_token_ids == expected_token_ids

    with pytest.raises(StopIteration):
        next(it)


def test_ngram_case_insensitive_first_token():
    """
    Test that the case sensitivity function works, when it is the first token.
    """
    c = load_from_file(fixture_location('long.conll'))
    results = list(find_ngrams(c, 'Il'.split(), case_sensitive=False))

    actual_ids = list(map(lambda res: res[0].id, results))
    actual_indices = list(map(operator.itemgetter(1), results))

    expected_ids = ['fr-ud-test_00003', 'fr-ud-test_00005', 'fr-ud-test_00008']
    expected_indices = [1, 16, 0]

    assert actual_ids == expected_ids
    assert actual_indices == expected_indices


def test_ngram_case_insensitive_n_token():
    """
    Test that the case sensitivity function works, when it is the nth token.
    """
    c = load_from_file(fixture_location('long.conll'))
    s, i, tokens = next(
        find_ngrams(
            c,
            'l\' orgaNisaTion pour La sécurité et la'.split(),
            case_sensitive=False))

    actual_token_ids = list(map(lambda token: token.id, tokens))
    expected_token_ids = ['9', '10', '11', '12', '13', '14', '15']

    assert s.id == 'fr-ud-test_00004'
    assert i == 8
    assert actual_token_ids == expected_token_ids


def test_no_nonprojectivities():
    """
    Test with a sentence with no non-projective dependencies.
    """
    c = load_from_file(fixture_location('projectivities.conll'))
    sent = c[0]
    deps = find_nonprojective_deps(sent)

    assert not deps


def test_simple_nonprojectivities():
    """
    Test logic with a sentence with one single non-projectivity.
    """
    c = load_from_file(fixture_location('projectivities.conll'))
    sent1 = c[1]
    deps1 = find_nonprojective_deps(sent1)

    sent2 = c[2]
    deps2 = find_nonprojective_deps(sent2)

    assert deps1 == [(sent1['16'], sent1['4'])]
    assert deps2 == [(sent2['8'], sent2['5'])]


def test_multiword_ignore():
    """
    Test that multiword tokens are ignored and do not cause errors.
    """
    c = load_from_file(fixture_location('projectivities.conll'))

    sent = c[3]
    deps = find_nonprojective_deps(sent)

    assert deps == [(sent['16'], sent['4'])]


def test_overlapping_nonprojectivities():
    """
    Test that multiple non-projectivities can overlap.
    """
    c = load_from_file(fixture_location('projectivities.conll'))

    sent = c[4]
    deps = find_nonprojective_deps(sent)

    assert set(deps) == set([(sent['16'], sent['4']), (sent['16'],
                                                       sent['11'])])


def test_multiple_nonprojectivities():
    """
    Test that multiple disjoint projectivities are properly identified.
    """
    c = load_from_file(fixture_location('projectivities.conll'))

    sent = c[5]
    deps = find_nonprojective_deps(sent)

    assert set(deps) == set([(sent['22'], sent['3']), (sent['22'], sent['21']),
                             (sent['28'], sent['25'])])


def test_simple_nonprojectivities():
    """
    Test logic with a sentence with one single non-projectivity.
    """
    c = load_from_file(fixture_location('projectivities.conll'))
    sent1 = c[3]
    deps1 = find_nonprojective_deps(sent1)

    sent2 = c[2]
    deps2 = find_nonprojective_deps(sent2)

    assert deps1 == [(sent1['16'], sent1['4'])]
    assert deps2 == [(sent2['8'], sent2['5'])]
