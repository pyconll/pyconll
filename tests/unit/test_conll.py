from pathlib import Path

from pyconll.parser import Parser
from pyconll.unit.conll import Conll
from pyconll.unit.token import Token
from tests.util import fixture_location


def load_conll(p: Path) -> Conll:
    parser = Parser(Token)
    sentences = parser.load_from_file(p)
    return Conll(sentences)


def test_string_output():
    """
    Test that the strings are properly created.
    """
    fixture = fixture_location("basic.conll")
    contents = fixture.read_text()
    conll = load_conll(fixture)

    assert contents == conll.conll()


def test_writing_output():
    """
    Test that CoNLL files are properly created.
    """
    basic_fixture = fixture_location("basic.conll")
    contents_basic = basic_fixture.read_text()
    conll = load_conll(basic_fixture)

    output_loc = fixture_location("output.conll")
    with open(output_loc, "w") as f:
        conll.write(f)

    contents_write = output_loc.read_text()
    output_loc.unlink()

    assert contents_basic == contents_write
