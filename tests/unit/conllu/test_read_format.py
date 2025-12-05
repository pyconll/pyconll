"""
Tests for CoNLL-U format parsing using the Format component.

These tests verify that the Format correctly handles CoNLL-U formatted data
from various sources (strings, files, resources) and handles edge cases like
different newline formats and whitespace handling.
"""

import pytest

from pyconll.conllu import ConlluFormat, Sentence

from tests.unit.util import assert_token_equivalence, fixture_location


def test_load_from_string(conllu_format: ConlluFormat):
    """
    Test that a CoNLL file can properly be loaded from a string.
    """
    contents = fixture_location("basic.conll").read_text("utf-8")
    c = conllu_format.load_from_string(contents)

    assert len(c) == 4

    assert len(c[0].tokens) == 10
    assert c[0].meta["sent_id"] == "fr-ud-dev_00001"

    assert len(c[1].tokens) == 14
    assert c[1].meta["sent_id"] == "fr-ud-dev_00002"
    assert c[1].tokens[9].form == "donc"

    assert len(c[2].tokens) == 9
    assert c[2].meta["sent_id"] == "fr-ud-dev_00003"

    assert len(c[3].tokens) == 52
    assert c[3].meta["sent_id"] == "fr-ud-dev_00004"


def test_load_from_file(conllu_format: ConlluFormat):
    """
    Test that a CoNLL file can properly be loaded from a filename.
    """
    c = conllu_format.load_from_file(fixture_location("basic.conll"))
    sent = c[1]

    assert len(c) == 4
    assert len(sent.tokens) == 14
    assert sent.tokens[9].form == "donc"


def test_load_from_windows_newline_file(conllu_format: ConlluFormat):
    """
    Test that a CoNLL file can properly be loaded from a filename with windows newlines.
    """
    c = conllu_format.load_from_file(fixture_location("newlines.conll"))
    sent = c[1]

    assert len(c) == 4
    assert len(sent.tokens) == 14
    assert sent.tokens[9].form == "donc"
    assert sent.tokens[9].misc == {}


def test_no_ending_newline(conllu_format: ConlluFormat):
    """
    Test correct creation when the ending of the file ends in no newline.
    """
    conll = conllu_format.load_from_file(fixture_location("no_newline.conll"))

    assert len(conll) == 3

    assert len(conll[0].tokens) == 10
    assert conll[0].meta["sent_id"] == "fr-ud-dev_00001"

    assert len(conll[1].tokens) == 14
    assert conll[1].meta["sent_id"] == "fr-ud-dev_00002"

    assert len(conll[2].tokens) == 9
    assert conll[2].meta["sent_id"] == "fr-ud-dev_00003"


def test_many_newlines(conllu_format: ConlluFormat):
    """
    Test correct Conll parsing when there are too many newlines.
    """
    conll = conllu_format.load_from_file(fixture_location("many_newlines.conll"))

    assert len(conll) == 4

    assert len(conll[0].tokens) == 10
    assert conll[0].meta["sent_id"] == "fr-ud-dev_00001"

    assert len(conll[1].tokens) == 14
    assert conll[1].meta["sent_id"] == "fr-ud-dev_00002"

    assert len(conll[2].tokens) == 9
    assert conll[2].meta["sent_id"] == "fr-ud-dev_00003"

    assert len(conll[3].tokens) == 52
    assert conll[3].meta["sent_id"] == "fr-ud-dev_00004"


def test_load_from_resource(conllu_format: ConlluFormat):
    """
    Test that a CoNLL file can properly be loaded from a string.
    """
    with open(fixture_location("basic.conll"), encoding="utf-8") as f:
        c = conllu_format.load_from_resource(f)
        sent = c[1]

        assert len(c) == 4
        assert len(sent.tokens) == 14
        assert sent.tokens[9].form == "donc"


def test_equivalence_across_load_operations(conllu_format: ConlluFormat):
    """
    Test that the Conll object created from a string, path, and resource is the same if
    the underlying source is the same.
    """
    contents = fixture_location("long.conll").read_text("utf-8")
    str_c = conllu_format.load_from_string(contents)
    file_c = conllu_format.load_from_file(fixture_location("long.conll"))

    with open(fixture_location("long.conll"), encoding="utf-8") as resource:
        resource_c = conllu_format.load_from_resource(resource)

    def assert_equivalent_conll_objs(conll1: list[Sentence], conll2: list[Sentence]) -> None:
        assert len(conll1) == len(conll1)
        for i in range(len(conll1)):
            assert conll1[i].meta["sent_id"] == conll2[i].meta["sent_id"]
            assert conll1[i].meta["text"] == conll2[i].meta["text"]

            assert len(conll1[i].tokens) == len(conll2[i].tokens)
            for j, token1 in enumerate(conll1[i].tokens):
                token2 = conll2[i].tokens[j]
                assert_token_equivalence(token1, token2)

    assert_equivalent_conll_objs(str_c, file_c)
    assert_equivalent_conll_objs(file_c, resource_c)


def test_iter_from_string(conllu_format: ConlluFormat):
    """
    Test that CoNLL files in string form can be iterated over without memory.
    """
    contents = fixture_location("basic.conll").read_text("utf-8")

    expected_ids = [f"fr-ud-dev_0000{i}" for i in range(1, 5)]
    actual_ids = [sent.meta["sent_id"] for sent in conllu_format.iter_from_string(contents)]

    assert expected_ids == actual_ids


def test_iter_from_file(conllu_format: ConlluFormat):
    """
    Test that CoNLL files can be iterated over without memory given the
    filename.
    """
    expected_ids = [f"fr-ud-dev_0000{i}" for i in range(1, 5)]
    actual_ids = [
        sent.meta["sent_id"]
        for sent in conllu_format.iter_from_file(fixture_location("basic.conll"))
    ]

    assert expected_ids == actual_ids


def test_iter_from_resource(conllu_format: ConlluFormat):
    """
    Test that an arbitrary resource can be iterated over.
    """
    with open(fixture_location("basic.conll"), encoding="utf-8") as f:
        expected_ids = [f"fr-ud-dev_0000{i}" for i in range(1, 5)]
        actual_ids = [sent.meta["sent_id"] for sent in conllu_format.iter_from_resource(f)]

        assert expected_ids == actual_ids


def test_invalid_conll(conllu_format: ConlluFormat):
    """
    Test that an invalid sentence results in an invalid Conll object.
    """
    with pytest.raises(ValueError):
        conllu_format.load_from_file(fixture_location("invalid.conll"))


def test_extra_whitespace_conll(conllu_format: ConlluFormat):
    """
    Test that extra spacing on a newline separating two sentences can be handled.
    """
    sentences = conllu_format.load_from_file(fixture_location("extra_whitespace.conll"))

    assert len(sentences) == 2
    assert sentences[0].meta["sent_id"] == "fr-ud-dev_00001"
    assert sentences[0].meta["text"] == "Aviator, un film sur la vie de Hughes."

    assert sentences[1].meta["sent_id"] == "fr-ud-dev_00002"
    assert (
        sentences[1].meta["text"]
        == "Les études durent six ans mais leur contenu diffère donc selon les Facultés."
    )
