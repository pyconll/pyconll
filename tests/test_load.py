import pytest

from pyconll import load_from_string, load_from_file, iter_from_string, iter_from_file
from pyconll.load import iter_from_compressed_file
from tests.util import fixture_location
from tests.unit.util import assert_token_members


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


def test_load_from_file_and_string_equivalence():
    """
    Test that the Conll object created from a string and file is the same if
    the underlying source is the same.
    """
    with open(fixture_location('long.conll'), encoding='utf-8') as f:
        contents = f.read()
    str_c = load_from_string(contents)
    file_c = load_from_file(fixture_location('long.conll'))

    assert len(str_c) == len(file_c)
    for i in range(len(str_c)):
        assert str_c[i].id == file_c[i].id
        assert str_c[i].text == file_c[i].text
        print(str_c[i].conll())
        print(file_c[i].conll())

        for str_token in str_c[i]:
            file_token = file_c[i][str_token.id]
            assert_token_members(str_token, file_token.id, file_token.form,
                                 file_token.lemma, file_token.upos,
                                 file_token.xpos, file_token.feats,
                                 file_token.head, file_token.deprel,
                                 file_token.deps, file_token.misc)


def test_iter_from_string():
    """
    Test that CoNLL files in string form can be iterated over without memory.
    """
    with open(fixture_location('basic.conll'), encoding='utf-8') as f:
        contents = f.read()

    expected_ids = ['fr-ud-dev_0000{}'.format(i) for i in range(1, 5)]
    actual_ids = [sent.id for sent in iter_from_string(contents)]

    assert expected_ids == actual_ids


def test_iter_from_file():
    """
    Test that CoNLL files can be iterated over without memory given the
    filename.
    """
    expected_ids = ['fr-ud-dev_0000{}'.format(i) for i in range(1, 5)]
    actual_ids = [
        sent.id for sent in iter_from_file(fixture_location('basic.conll'))
    ]

    assert expected_ids == actual_ids


def test_iter_from_compressed_file():
    """
    Test that compressed CoNLL files (.xz) can be iterated over without
    memory given the filename.
    """
    expected_ids = ['fr-ud-dev_0000{}'.format(i) for i in range(1, 5)]
    actual_ids = [
        sent.id for sent in iter_from_compressed_file(fixture_location('basic.conll.xz'))
    ]

    assert expected_ids == actual_ids