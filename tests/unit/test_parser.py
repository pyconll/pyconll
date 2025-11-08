from typing import Optional
import pytest
from pyconll import Parser
from pyconll.schema import TokenProtocol, nullable
from pyconll.unit.sentence import Sentence
from pyconll.unit.token import Token
from tests.unit.util import assert_token_equivalence, fixture_location

conll_parser = Parser(Token)


def test_load_from_string():
    """
    Test that a CoNLL file can properly be loaded from a string.
    """
    contents = fixture_location("basic.conll").read_text("utf-8")
    c = conll_parser.load_from_string(contents)

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


def test_load_from_file():
    """
    Test that a CoNLL file can properly be loaded from a filename.
    """
    c = conll_parser.load_from_file(fixture_location("basic.conll"))
    sent = c[1]

    assert len(c) == 4
    assert len(sent.tokens) == 14
    assert sent.tokens[9].form == "donc"


def test_load_from_windows_newline_file():
    """
    Test that a CoNLL file can properly be loaded from a filename with windows newlines.
    """
    c = conll_parser.load_from_file(fixture_location("newlines.conll"))
    sent = c[1]

    assert len(c) == 4
    assert len(sent.tokens) == 14
    assert sent.tokens[9].form == "donc"
    assert sent.tokens[9].misc == {}


def test_no_ending_newline():
    """
    Test correct creation when the ending of the file ends in no newline.
    """
    conll = conll_parser.load_from_file(fixture_location("no_newline.conll"))

    assert len(conll) == 3

    assert len(conll[0].tokens) == 10
    assert conll[0].meta["sent_id"] == "fr-ud-dev_00001"

    assert len(conll[1].tokens) == 14
    assert conll[1].meta["sent_id"] == "fr-ud-dev_00002"

    assert len(conll[2].tokens) == 9
    assert conll[2].meta["sent_id"] == "fr-ud-dev_00003"


def test_many_newlines():
    """
    Test correct Conll parsing when there are too many newlines.
    """
    conll = conll_parser.load_from_file(fixture_location("many_newlines.conll"))

    assert len(conll) == 4

    assert len(conll[0].tokens) == 10
    assert conll[0].meta["sent_id"] == "fr-ud-dev_00001"

    assert len(conll[1].tokens) == 14
    assert conll[1].meta["sent_id"] == "fr-ud-dev_00002"

    assert len(conll[2].tokens) == 9
    assert conll[2].meta["sent_id"] == "fr-ud-dev_00003"

    assert len(conll[3].tokens) == 52
    assert conll[3].meta["sent_id"] == "fr-ud-dev_00004"


def test_load_from_resource():
    """
    Test that a CoNLL file can properly be loaded from a string.
    """
    with open(fixture_location("basic.conll"), encoding="utf-8") as f:
        c = conll_parser.load_from_resource(f)
        sent = c[1]

        assert len(c) == 4
        assert len(sent.tokens) == 14
        assert sent.tokens[9].form == "donc"


def test_equivalence_across_load_operations():
    """
    Test that the Conll object created from a string, path, and resource is the same if
    the underlying source is the same.
    """
    contents = fixture_location("long.conll").read_text("utf-8")
    str_c = conll_parser.load_from_string(contents)
    file_c = conll_parser.load_from_file(fixture_location("long.conll"))

    with open(fixture_location("long.conll"), encoding="utf-8") as resource:
        resource_c = conll_parser.load_from_resource(resource)

    def assert_equivalent_conll_objs(
        conll1: list[Sentence[Token]], conll2: list[Sentence[Token]]
    ) -> None:
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


def test_iter_from_string():
    """
    Test that CoNLL files in string form can be iterated over without memory.
    """
    contents = fixture_location("basic.conll").read_text("utf-8")

    expected_ids = [f"fr-ud-dev_0000{i}" for i in range(1, 5)]
    actual_ids = [sent.meta["sent_id"] for sent in conll_parser.iter_from_string(contents)]

    assert expected_ids == actual_ids


def test_iter_from_file():
    """
    Test that CoNLL files can be iterated over without memory given the
    filename.
    """
    expected_ids = [f"fr-ud-dev_0000{i}" for i in range(1, 5)]
    actual_ids = [
        sent.meta["sent_id"]
        for sent in conll_parser.iter_from_file(fixture_location("basic.conll"))
    ]

    assert expected_ids == actual_ids


def test_iter_from_resource():
    """
    Test that an arbitrary resource can be iterated over.
    """
    with open(fixture_location("basic.conll"), encoding="utf-8") as f:
        expected_ids = [f"fr-ud-dev_0000{i}" for i in range(1, 5)]
        actual_ids = [sent.meta["sent_id"] for sent in conll_parser.iter_from_resource(f)]

        assert expected_ids == actual_ids


def test_invalid_conll():
    """
    Test that an invalid sentence results in an invalid Conll object.
    """
    with pytest.raises(ValueError):
        c = conll_parser.load_from_file(fixture_location("invalid.conll"))


def test_extra_whitespace_conll():
    """
    Test that extra spacing on a newline separating two sentences can be handled.
    """
    sentences = conll_parser.load_from_file(fixture_location("extra_whitespace.conll"))

    assert len(sentences) == 2
    assert sentences[0].meta["sent_id"] == "fr-ud-dev_00001"
    assert sentences[0].meta["text"] == "Aviator, un film sur la vie de Hughes."

    assert sentences[1].meta["sent_id"] == "fr-ud-dev_00002"
    assert (
        sentences[1].meta["text"]
        == "Les études durent six ans mais leur contenu diffère donc selon les Facultés."
    )


def test_custom_token_parsing():
    """
    Test that a custom token type can be used with the parser.
    """

    class TestToken(TokenProtocol):
        id: str
        category: int
        body: Optional[str] = nullable(str, "_")

    p = Parser(TestToken)

    source = (
        "1\t2\tSomething random.\n"
        "2\t3\tAnother thing but not as random.\n"
        "\n"
        "1\t0\tA repeat.\n"
        "2\t0\tNow something unique.\n"
        "3\t1\t_\n"
        "\n"
    )

    def as_tup(t: TestToken):
        return (t.id, t.category, t.body)

    sentences = p.load_from_string(source)

    f = sentences[0]
    assert as_tup(f.tokens[0]) == ("1", 2, "Something random.")
    assert as_tup(f.tokens[1]) == ("2", 3, "Another thing but not as random.")

    s = sentences[1]
    assert as_tup(s.tokens[0]) == ("1", 0, "A repeat.")
    assert as_tup(s.tokens[1]) == ("2", 0, "Now something unique.")
    assert as_tup(s.tokens[2]) == ("3", 1, None)
