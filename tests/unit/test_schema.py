"""Tests that various (non CoNLL-U) Token protocols properly compile"""

import sys
from typing import Optional
import pytest
from pyconll.schema import (
    TokenSchema,
    mapping,
    field,
    via,
    varcols,
    nullable,
)
from pyconll import _compile


def test_simple_primitive_schema():
    """
    Test that a token schema with primitive types (int, str, float) compiles correctly.
    """

    class SimpleToken(TokenSchema):
        id: int
        name: str
        score: float

    parser = _compile.token_parser(SimpleToken, "\t", False)
    serializer = _compile.token_serializer(SimpleToken, "\t")

    raw_line = "3\tthe value of pi\t3.14"
    token = parser(raw_line)

    assert serializer(token) == raw_line

    assert token.id == 3
    assert token.name == "the value of pi"
    assert token.score == 3.14


def test_invalid_primitive_schema():
    """
    Test that a token schema with unsupported types (like bare list) raises an exception.
    """

    class InvalidToken(TokenSchema):
        id: int
        name: str
        scores: list[float]

    with pytest.raises(Exception):
        _compile.token_parser(InvalidToken, "\t", False)

    with pytest.raises(Exception):
        _compile.token_serializer(InvalidToken, "\t")


def test_invalid_schema_attribute():
    """
    Test that using a raw lambda instead of a field descriptor raises an exception.
    """

    class InvalidToken(TokenSchema):
        id: int
        name: str
        scores: list[float] = lambda s: map(float, s.split(","))

    with pytest.raises(Exception):
        _compile.token_parser(InvalidToken, "\t", False)

    with pytest.raises(Exception):
        _compile.token_serializer(InvalidToken, "\t")


def test_via_descriptor_schema():
    """
    Test that via descriptors work correctly for string interning and nested descriptors.
    """

    class MemoryEfficientToken(TokenSchema):
        id: int
        form: str = field(via(sys.intern, str))
        lemma: str = field(via(sys.intern, str))
        feats: dict[str, str] = field(mapping(str, via(sys.intern, str), "|", "=", "_"))

    parser = _compile.token_parser(MemoryEfficientToken, "\t", False)
    serializer = _compile.token_serializer(MemoryEfficientToken, "\t")

    token_line1 = "3\tthe\tthe\t_"
    token_line2 = "4\tcats\tcat\tArticle=the|Definite=Yes"

    token1 = parser(token_line1)
    token2 = parser(token_line2)

    assert id(token1.form) == id(token1.lemma)
    assert id(token1.form) == id(token2.feats["Article"])

    assert token_line1 == serializer(token1)
    assert token_line2 == serializer(token2)


def test_via_descriptor_optimizations():
    """
    Test that via descriptors with custom serialization functions work correctly.
    """

    class ViaProtocol(TokenSchema):
        id: int = field(via(int, str))
        form: str = field(via(str, repr))

    parser = _compile.token_parser(ViaProtocol, "\t", False)
    serializer = _compile.token_serializer(ViaProtocol, "\t")

    line = "3\tcat"
    token = parser(line)

    assert serializer(token) == "3\t'cat'"


def test_varcols_schema_str():
    """
    Test that a token schema with varcols for strings compiles correctly.
    """

    class VarColsToken(TokenSchema):
        id: int
        name: str
        extra: list[str] = field(varcols(str))

    parser = _compile.token_parser(VarColsToken, "\t", False)
    serializer = _compile.token_serializer(VarColsToken, "\t")

    raw_line = "1\tword\ta\tb\tc"
    token = parser(raw_line)

    assert token.id == 1
    assert token.name == "word"
    assert token.extra == ["a", "b", "c"]
    assert serializer(token) == raw_line


def test_varcols_schema_int():
    """
    Test that a token schema with varcols for ints compiles correctly.
    """

    class VarColsIntToken(TokenSchema):
        prefix: str
        values: list[int] = field(varcols(int))

    parser = _compile.token_parser(VarColsIntToken, "\t", False)
    serializer = _compile.token_serializer(VarColsIntToken, "\t")

    raw_line = "data\t10\t20\t30"
    token = parser(raw_line)

    assert token.prefix == "data"
    assert token.values == [10, 20, 30]
    assert serializer(token) == raw_line


def test_varcols_schema_empty():
    """
    Test that a token schema with varcols handles zero variable columns.
    """

    class VarColsToken(TokenSchema):
        id: int
        extras: list[str] = field(varcols(str))

    parser = _compile.token_parser(VarColsToken, "\t", False)
    serializer = _compile.token_serializer(VarColsToken, "\t")

    raw_line = "5"
    token = parser(raw_line)

    assert token.id == 5
    assert token.extras == []
    assert serializer(token) == raw_line


def test_varcols_schema_with_nullable():
    """
    Test that a token schema with varcols and nullable elements compiles correctly.
    """

    class VarColsNullableToken(TokenSchema):
        name: str
        scores: list[Optional[int]] = field(varcols(nullable(int, "_")))

    parser = _compile.token_parser(VarColsNullableToken, "\t", False)
    serializer = _compile.token_serializer(VarColsNullableToken, "\t")

    raw_line = "test\t10\t_\t30"
    token = parser(raw_line)

    assert token.name == "test"
    assert token.scores == [10, None, 30]
    assert serializer(token) == raw_line


def test_varcols_schema_with_trailing_fixed_cols():
    """
    Test that a token schema with varcols followed by fixed columns compiles correctly.
    """

    class VarColsWithTrailingToken(TokenSchema):
        id: int
        middle: list[str] = field(varcols(str))
        status: str

    parser = _compile.token_parser(VarColsWithTrailingToken, "\t", False)
    serializer = _compile.token_serializer(VarColsWithTrailingToken, "\t")

    raw_line = "1\ta\tb\tc\tdone"
    token = parser(raw_line)

    assert token.id == 1
    assert token.middle == ["a", "b", "c"]
    assert token.status == "done"
    assert serializer(token) == raw_line


def test_varcols_schema_multiple_varcols_error():
    """
    Test that a token schema with multiple varcols fields raises an error.
    """

    class InvalidToken(TokenSchema):
        first: list[str] = field(varcols(str))
        second: list[int] = field(varcols(int))

    with pytest.raises(RuntimeError, match="more than one varcols"):
        _compile.token_parser(InvalidToken, "\t", False)
