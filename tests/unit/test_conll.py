import io

from pyconll import conllu
from tests.unit.util import fixture_location


def test_string_output():
    """
    Test that the strings are properly created.
    """
    fixture = fixture_location("basic.conll")
    original = fixture.read_text()

    sentences = conllu.parser.load_from_string(original)

    # TODO: How does
    buffer = io.StringIO()
    conllu.serializer.write_corpus(sentences, buffer)
    serialized = buffer.getvalue()

    assert original == serialized
