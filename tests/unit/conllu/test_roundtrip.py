"""
Tests for CoNLL-U corpus roundtrip consistency.

These tests verify that reading a CoNLL-U file and then serializing it back
produces identical output, ensuring format preservation.
"""

import io

from pyconll.conllu import ConlluFormat
from tests.unit.util import fixture_location


def test_string_output(conllu_format: ConlluFormat):
    """
    Test that the strings are properly created.
    """
    fixture = fixture_location("basic.conll")
    original = fixture.read_text()

    sentences = conllu_format.load_from_string(original)

    buffer = io.StringIO()
    conllu_format.write_corpus(sentences, buffer)
    serialized = buffer.getvalue()

    assert original == serialized
