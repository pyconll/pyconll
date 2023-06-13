import pytest

from pyconll import load_from_string, load_from_file, load_from_resource, iter_from_string, iter_from_file, iter_from_resource
from tests.util import fixture_location
from tests.unit.util import assert_token_equivalence


def test_load_from_string():
    """
    Test that a CoNLL file can properly be loaded from a string.
    """
    with open(fixture_location('basic.conll'), encoding='utf-8') as f:
        contents = f.read()

    c = load_from_string(contents)
    sent = c[1]

    assert len(c) == 4
    assert len(sent) == 14
    assert sent['10'].form == 'donc'


def test_load_from_file():
    """
    Test that a CoNLL file can properly be loaded from a filename.
    """
    c = load_from_file(fixture_location('basic.conll'))
    sent = c[1]

    assert len(c) == 4
    assert len(sent) == 14
    assert sent['10'].form == 'donc'


def test_load_from_resource():
    """
    Test that a CoNLL file can properly be loaded from a string.
    """
    with open(fixture_location('basic.conll'), encoding='utf-8') as f:
        c = load_from_resource(f)
        sent = c[1]

        assert len(c) == 4
        assert len(sent) == 14
        assert sent['10'].form == 'donc'


def test_equivalence_across_load_operations():
    """
    Test that the Conll object created from a string, path, and resource is the same if
    the underlying source is the same.
    """
    with open(fixture_location('long.conll'), encoding='utf-8') as f:
        contents = f.read()
    str_c = load_from_string(contents)
    file_c = load_from_file(fixture_location('long.conll'))

    with open(fixture_location('long.conll'), encoding='utf-8') as resource:
        resource_c = load_from_resource(resource)

    def assert_equivalent_conll_objs(conll1, conll2):
        assert len(conll1) == len(conll1)
        for i in range(len(conll1)):
            assert len(conll1[i]) == len(conll2[i])
            assert conll1[i].id == conll2[i].id
            assert conll1[i].text == conll2[i].text

            for token1 in conll1[i]:
                token2 = conll2[i][token1.id]
                assert_token_equivalence(token1, token2)

    assert_equivalent_conll_objs(str_c, file_c)
    assert_equivalent_conll_objs(file_c, resource_c)


def test_iter_from_string():
    """
    Test that CoNLL files in string form can be iterated over without memory.
    """
    with open(fixture_location('basic.conll'), encoding='utf-8') as f:
        contents = f.read()

    expected_ids = [f'fr-ud-dev_0000{i}' for i in range(1, 5)]
    actual_ids = [sent.id for sent in iter_from_string(contents)]

    assert expected_ids == actual_ids


def test_iter_from_file():
    """
    Test that CoNLL files can be iterated over without memory given the
    filename.
    """
    expected_ids = [f'fr-ud-dev_0000{i}' for i in range(1, 5)]
    actual_ids = [
        sent.id for sent in iter_from_file(fixture_location('basic.conll'))
    ]

    assert expected_ids == actual_ids


def test_iter_from_resource():
    """
    Test that an arbitrary resource can be iterated over.
    """
    with open(fixture_location('basic.conll'), encoding='utf-8') as f:
        expected_ids = [f'fr-ud-dev_0000{i}' for i in range(1, 5)]
        actual_ids = [sent.id for sent in iter_from_resource(f)]

        assert expected_ids == actual_ids
