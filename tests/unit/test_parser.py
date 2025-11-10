"""
Tests for the generic Parser component.

These tests verify that the Parser can handle custom token schemas beyond
the standard CoNLL-U format, demonstrating the parser's flexibility.
"""

from typing import Optional

import pytest

from pyconll.exception import ParseError
from pyconll.parser import Parser
from pyconll.schema import TokenSchema, nullable


def test_custom_token_parsing():
    """
    Test that a custom token type can be used with the parser.
    """

    class TestToken(TokenSchema):
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


def test_middle_sentence_comment_fails():
    """
    Test that a comment that appears in the middle of a sentence (after Tokens have already
    started), is not valid.
    """

    class TestToken(TokenSchema):
        id: str
        category: int
        body: Optional[str] = nullable(str, "_")

    p = Parser(TestToken)

    source = (
        "# comment1\n"
        "1\t2\tSomething random.\n"
        "2\t3\tAnother thing but not as random.\n"
        "\n"
        "# comment2 = 2\n"
        "1\t0\tA repeat.\n"
        "2\t0\tNow something unique.\n"
        "# comment3 = 3\n"
        "3\t1\t_\n"
        "\n"
    )

    with pytest.raises(ParseError):
        p.load_from_string(source)
