"""Tests that various (non CoNLL-U) Token protocols properly compile"""

import sys
from typing import Optional
import pytest
from pyconll.schema import (
    field,
    mapping,
    nullable,
    tokenspec,
    varcols,
    via,
)
from pyconll import _compile


def test_simple_primitive_schema():
    """
    Test that a token schema with primitive types (int, str, float) compiles correctly.
    """

    @tokenspec
    class SimpleToken:
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

    @tokenspec
    class InvalidToken:
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

    @tokenspec
    class InvalidToken:
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

    @tokenspec
    class MemoryEfficientToken:
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

    @tokenspec
    class ViaProtocol:
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

    @tokenspec
    class VarColsToken:
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

    @tokenspec
    class VarColsIntToken:
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

    @tokenspec
    class VarColsToken:
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

    @tokenspec
    class VarColsNullableToken:
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

    @tokenspec
    class VarColsWithTrailingToken:
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

    @tokenspec
    class InvalidToken:
        first: list[str] = field(varcols(str))
        second: list[int] = field(varcols(int))

    with pytest.raises(RuntimeError, match="more than one varcols"):
        _compile.token_parser(InvalidToken, "\t", False)


def test_collapse_repeated_delimiters_basic():
    """
    Test that repeated delimiters can be collapsed into a single delimiter.
    """

    @tokenspec
    class SimpleToken:
        id: int
        name: str
        value: float

    parser = _compile.token_parser(SimpleToken, "\t", True)
    serializer = _compile.token_serializer(SimpleToken, "\t")

    # Line with multiple consecutive tabs
    raw_line_with_repeats = "5\t\t\tword\t\t3.14"
    token = parser(raw_line_with_repeats)

    assert token.id == 5
    assert token.name == "word"
    assert token.value == 3.14

    # Serialization uses single delimiter
    assert serializer(token) == "5\tword\t3.14"


def test_collapse_with_space_delimiter():
    """
    Test that collapse works with space as delimiter.
    """

    @tokenspec
    class SpaceDelimitedToken:
        word: str
        count: int

    parser = _compile.token_parser(SpaceDelimitedToken, " ", True)

    # Multiple spaces between fields
    raw_line = "hello    42"
    token = parser(raw_line)

    assert token.word == "hello"
    assert token.count == 42


def test_collapse_with_varcols():
    """
    Test that collapse works correctly with variable columns.
    """

    @tokenspec
    class VarColsToken:
        id: int
        extras: list[str] = field(varcols(str))
        status: str

    parser = _compile.token_parser(VarColsToken, "\t", True)
    serializer = _compile.token_serializer(VarColsToken, "\t")

    # Line with repeated delimiters
    raw_line = "1\t\ta\t\tb\t\tc\t\tdone"
    token = parser(raw_line)

    assert token.id == 1
    assert token.extras == ["a", "b", "c"]
    assert token.status == "done"

    # Serialization normalizes to single delimiters
    assert serializer(token) == "1\ta\tb\tc\tdone"


def test_collapse_with_nullable_fields():
    """
    Test that collapse works with nullable field descriptors.
    """

    @tokenspec
    class NullableToken:
        name: str
        score: Optional[int] = field(nullable(int, "_"))
        value: Optional[float] = field(nullable(float, "N/A"))

    parser = _compile.token_parser(NullableToken, "\t", True)
    serializer = _compile.token_serializer(NullableToken, "\t")

    # With repeated delimiters and null values
    raw_line = "test\t\t_\t\tN/A"
    token = parser(raw_line)

    assert token.name == "test"
    assert token.score is None
    assert token.value is None

    assert serializer(token) == "test\t_\tN/A"


def test_collapse_varying_delimiter_counts():
    """
    Test collapse with different numbers of delimiters between columns.
    """

    @tokenspec
    class Token5Cols:
        a: str
        b: str
        c: str
        d: str
        e: str

    parser = _compile.token_parser(Token5Cols, "|", True)

    # Varying numbers of delimiters between fields
    raw_line = "start|||||end||||middle|||x|||y"
    token = parser(raw_line)

    assert token.a == "start"
    assert token.b == "end"
    assert token.c == "middle"
    assert token.d == "x"
    assert token.e == "y"


def test_collapse_with_mapping_descriptor():
    """
    Test that collapse works with mapping field descriptors.
    """

    @tokenspec
    class MappingToken:
        id: int
        features: dict[str, str] = field(mapping(str, str, "|", "=", "_"))

    parser = _compile.token_parser(MappingToken, "\t", True)

    # Multiple tabs before the features column
    raw_line = "10\t\t\tkey1=val1|key2=val2"
    token = parser(raw_line)

    assert token.id == 10
    assert token.features == {"key1": "val1", "key2": "val2"}


def test_extra_primitives():
    """
    Test that extra primitives can be added on the Token class definition.
    """

    @tokenspec(extra_primitives=[set[str]])
    class WeirdToken:
        id: int
        chars: set[str]

    parser = _compile.token_parser(WeirdToken, "\t", False)

    raw_line = "10\tabcdefg"

    token = parser(raw_line)

    assert (token.id, token.chars) == (10, { "a", "b", "c", "d", "e", "f", "g"})
