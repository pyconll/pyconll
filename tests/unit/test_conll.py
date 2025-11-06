import io

from pyconll.parser import Parser
from pyconll.serializer import Serializer
from pyconll.unit.token import Token
from tests.util import fixture_location

_conllu_parser = Parser(Token)
_conllu_serializer = Serializer(Token)


def test_string_output():
    """
    Test that the strings are properly created.
    """
    fixture = fixture_location("basic.conll")
    original = fixture.read_text()

    sentences = _conllu_parser.load_from_string(original)

    # TODO: How does
    buffer = io.StringIO()
    _conllu_serializer.write_corpus(sentences, buffer)
    serialized = buffer.getvalue()

    assert original == serialized
