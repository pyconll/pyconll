"""Tests that various (non CoNLL-U) Token protocols properly compile"""

import sys
import pytest
from pyconll.schema import (
    TokenSchema,
    compile_token_parser,
    compile_token_serializer,
    mapping,
    nullable,
    field,
    via,
)


def test_simple_primitive_schema():
    class SimpleToken(TokenSchema):
        id: int
        name: str
        score: float

    parser = compile_token_parser(SimpleToken)
    serializer = compile_token_serializer(SimpleToken)

    raw_line = "3\tthe value of pi\t3.14"
    token = parser(raw_line, "\t")

    assert serializer(token, "\t") == raw_line

    assert token.id == 3
    assert token.name == "the value of pi"
    assert token.score == 3.14


def test_invalid_primitive_schema():
    class InvalidToken(TokenSchema):
        id: int
        name: str
        scores: list[float]

    with pytest.raises(Exception):
        compile_token_parser(InvalidToken)

    with pytest.raises(Exception):
        compile_token_serializer(InvalidToken)


def test_invalid_schema_attribute():
    class InvalidToken(TokenSchema):
        id: int
        name: str
        scores: list[float] = lambda s: map(float, s.split(","))

    with pytest.raises(Exception):
        compile_token_parser(InvalidToken)

    with pytest.raises(Exception):
        compile_token_serializer(InvalidToken)


def test_via_descriptor_schema():
    class MemoryEfficientToken(TokenSchema):
        id: int
        form: str = field(via(sys.intern, str))
        lemma: str = field(via(sys.intern, str))
        feats: dict[str, str] = field(mapping(str, via(sys.intern, str), "|", "=", "_"))

    parser = compile_token_parser(MemoryEfficientToken)
    serializer = compile_token_serializer(MemoryEfficientToken)

    token_line1 = "3\tthe\tthe\t_"
    token_line2 = "4\tcats\tcat\tArticle=the|Definite=Yes"

    token1 = parser(token_line1, "\t")
    token2 = parser(token_line2, "\t")

    assert id(token1.form) == id(token1.lemma)
    assert id(token1.form) == id(token2.feats["Article"])

    assert token_line1 == serializer(token1, "\t")
    assert token_line2 == serializer(token2, "\t")


def test_via_descriptor_optimizations():
    class ViaProtocol(TokenSchema):
        id: int = field(via(int, str))
        form: str = field(via(str, repr))

    parser = compile_token_parser(ViaProtocol)
    serializer = compile_token_serializer(ViaProtocol)

    line = "3\tcat"
    token = parser(line, "\t")

    assert serializer(token, "\t") == "3\t'cat'"
