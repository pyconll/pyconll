from pyconll import Parser
from pyconll.unit.conll import Conll
from tests.util import fixture_location
from tests.unit.util import assert_token_equivalence


def test_load_from_string():
    """
    Test that a CoNLL file can properly be loaded from a string.
    """
    contents = fixture_location("basic.conll").read_text("utf-8")
    c = Parser().load_from_string(contents)
    sent = c[1]

    assert len(c) == 4
    assert len(sent) == 14
    assert sent["10"].form == "donc"


def test_load_from_file():
    """
    Test that a CoNLL file can properly be loaded from a filename.
    """
    c = Parser().load_from_file(fixture_location("basic.conll"))
    sent = c[1]

    assert len(c) == 4
    assert len(sent) == 14
    assert sent["10"].form == "donc"


def test_load_from_resource():
    """
    Test that a CoNLL file can properly be loaded from a string.
    """
    with open(fixture_location("basic.conll"), encoding="utf-8") as f:
        c = Parser().load_from_resource(f)
        sent = c[1]

        assert len(c) == 4
        assert len(sent) == 14
        assert sent["10"].form == "donc"


def test_equivalence_across_load_operations():
    """
    Test that the Conll object created from a string, path, and resource is the same if
    the underlying source is the same.
    """
    contents = fixture_location("long.conll").read_text("utf-8")
    parser = Parser()
    str_c = parser.load_from_string(contents)
    file_c = parser.load_from_file(fixture_location("long.conll"))

    with open(fixture_location("long.conll"), encoding="utf-8") as resource:
        resource_c = parser.load_from_resource(resource)

    def assert_equivalent_conll_objs(conll1: Conll, conll2: Conll) -> None:
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
    contents = fixture_location("basic.conll").read_text("utf-8")
    parser = Parser()

    expected_ids = [f"fr-ud-dev_0000{i}" for i in range(1, 5)]
    actual_ids = [sent.id for sent in parser.iter_from_string(contents)]

    assert expected_ids == actual_ids


def test_iter_from_file():
    """
    Test that CoNLL files can be iterated over without memory given the
    filename.
    """
    expected_ids = [f"fr-ud-dev_0000{i}" for i in range(1, 5)]
    actual_ids = [sent.id for sent in Parser().iter_from_file(fixture_location("basic.conll"))]

    assert expected_ids == actual_ids


def test_iter_from_resource():
    """
    Test that an arbitrary resource can be iterated over.
    """
    with open(fixture_location("basic.conll"), encoding="utf-8") as f:
        expected_ids = [f"fr-ud-dev_0000{i}" for i in range(1, 5)]
        actual_ids = [sent.id for sent in Parser().iter_from_resource(f)]

        assert expected_ids == actual_ids
