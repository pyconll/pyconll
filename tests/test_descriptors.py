"""
Tests for schema descriptor factory methods.
"""

import sys
from typing import Any
import pytest

from pyconll.exception import ParseError
from pyconll.schema import (
    SchemaDescriptor,
    TokenProtocol,
    compile_token_parser,
    compile_token_serializer,
    nullable,
    array,
    fixed_array,
    schema,
    unique_array,
    mapping,
    via,
)


def _get_base_namespace() -> dict[str, Any]:
    return {"ParseError": ParseError}


def assert_conversions[T](desc: SchemaDescriptor[T], val: T, raw: str) -> None:
    """
    Helper to test both serialization and deserialization.

    Args:
        desc: The schema descriptor to test.
        val: The expected in-memory value.
        raw: The expected serialized string representation.
    """
    namespace = _get_base_namespace()
    deser_name = desc.deserialize_codegen(namespace)
    ser_name = desc.serialize_codegen(namespace)
    assert namespace[deser_name](raw) == val
    assert namespace[ser_name](val) == raw


def assert_deserialization[T](desc: SchemaDescriptor[T], raw: str, expected: T) -> None:
    """
    Helper to test only deserialization.

    Args:
        desc: The schema descriptor to test.
        raw: The serialized string representation.
        expected: The expected in-memory value.
    """
    namespace = _get_base_namespace()
    deser_name = desc.deserialize_codegen(namespace)
    assert namespace[deser_name](raw) == expected


def assert_serialization[T](desc: SchemaDescriptor[T], val: T, expected: str) -> None:
    """
    Helper to test only serialization.

    Args:
        desc: The schema descriptor to test.
        val: The in-memory value.
        expected: The expected serialized string representation.
    """
    namespace = _get_base_namespace()
    ser_name = desc.serialize_codegen(namespace)
    assert namespace[ser_name](val) == expected


def assert_serialization_error[T](desc: SchemaDescriptor[T], val: T) -> None:
    """
    Helper to test that serialization fails.

    Args:
        desc: The schema descriptor to test.
        val: The serialized string representation that should cause an error.
    """
    namespace = _get_base_namespace()
    with pytest.raises(Exception):
        ser_name = desc.serialize_codegen(namespace)
        namespace[ser_name](val)


def assert_deserialization_error[T](desc: SchemaDescriptor[T], raw: str) -> None:
    """
    Helper to test that deserialization fails.

    Args:
        desc: The schema descriptor to test.
        raw: The serialized string representation that should cause an error.
    """
    namespace = _get_base_namespace()
    with pytest.raises(Exception):
        deser_name = desc.deserialize_codegen(namespace)
        namespace[deser_name](raw)


class TestNullable:
    """Tests for the nullable factory method."""

    def test_nullable_int_with_default_empty_marker(self):
        """Test nullable int with default empty marker."""
        desc = nullable(int)
        assert_conversions(desc, None, "")
        assert_conversions(desc, 42, "42")
        assert_conversions(desc, -1, "-1")
        assert_conversions(desc, 0, "0")

    def test_nullable_int_with_custom_empty_marker(self):
        """Test nullable int with custom empty marker."""
        desc = nullable(int, empty_marker="_")
        assert_conversions(desc, None, "_")
        assert_conversions(desc, 42, "42")

    def test_nullable_float(self):
        """Test nullable float."""
        desc = nullable(float)
        assert_conversions(desc, None, "")
        assert_conversions(desc, 3.14, "3.14")
        assert_deserialization_error(desc, ".")

    def test_nullable_str(self):
        """Test nullable str."""
        desc = nullable(str, empty_marker="NONE")
        assert_conversions(desc, None, "NONE")
        assert_conversions(desc, "hello", "hello")

    def test_nullable_array(self):
        """Test nullable with nested array descriptor."""
        desc = nullable(array(int, "|"))
        assert_conversions(desc, None, "")
        assert_conversions(desc, [1, 2, 3], "1|2|3")

    def test_nullable_array_custom_empty_marker(self):
        """Test nullable descriptor wrapping an array descriptor with custom empty marker."""
        desc = nullable(array(int, ","), "_")
        assert_conversions(desc, None, "_")
        assert_conversions(desc, [], "")
        assert_conversions(desc, [1, 2, 3], "1,2,3")

    def test_nullable_mapping(self):
        """Test nullable descriptor wrapping a mapping descriptor."""
        desc = nullable(mapping(str, int, "|", "=", ordering_key=lambda x: x[0]), "_")
        assert_conversions(desc, None, "_")
        assert_conversions(desc, {"a": 1, "b": 2}, "a=1|b=2")

    def test_nullable_invalid_base_type(self):
        """Test nullable descriptor wrapping an invalid type."""
        desc = nullable(dict)
        assert_deserialization_error(desc, "")
        assert_serialization_error(desc, {})


class TestArray:
    """Tests for the array factory method."""

    def test_array_str(self):
        """Test array of strings."""
        desc = array(str, "|")
        assert_conversions(desc, [], "")
        assert_conversions(desc, ["a", "b", "c"], "a|b|c")

    def test_array_int(self):
        """Test array of ints."""
        desc = array(int, ",")
        assert_conversions(desc, [], "")
        assert_conversions(desc, [1, 2, 3], "1,2,3")

    def test_array_float(self):
        """Test array of floats."""
        desc = array(float, ";")
        assert_conversions(desc, [], "")
        assert_conversions(desc, [1.5, 2.5, 3.5], "1.5;2.5;3.5")

    def test_array_with_custom_empty_marker(self):
        """Test array with custom empty marker."""
        desc = array(str, "|", empty_marker="_")
        assert_conversions(desc, [], "_")

    def test_array_of_nullable(self):
        """Test array with nested nullable descriptor."""
        desc = array(nullable(int, "_"), "|")
        assert_conversions(desc, [], "")
        assert_conversions(desc, [1, None, 3], "1|_|3")

    def test_array_of_nullable_commas(self):
        """Test array of nullable elements with comma delimiter."""
        desc = array(nullable(int, "_"), ",")
        assert_conversions(desc, [1, None, 3], "1,_,3")


class TestFixedArray:
    """Tests for the fixed_array factory method."""

    def test_fixed_array_str(self):
        """Test fixed_array of strings."""
        desc = fixed_array(str, "|")
        assert_conversions(desc, (), "")
        assert_conversions(desc, ("a", "b", "c"), "a|b|c")

    def test_fixed_array_int(self):
        """Test fixed_array of ints."""
        desc = fixed_array(int, ",")
        assert_conversions(desc, (), "")
        assert_conversions(desc, (1, 2, 3), "1,2,3")

    def test_fixed_array_with_custom_empty_marker(self):
        """Test fixed_array with custom empty marker."""
        desc = fixed_array(str, "|", empty_marker="_")
        assert_conversions(desc, (), "_")

    def test_fixed_array_of_nullable(self):
        """Test fixed_array with nested nullable descriptor."""
        desc = fixed_array(nullable(int, "_"), "|")
        assert_conversions(desc, (), "")
        assert_conversions(desc, (1, None, 3), "1|_|3")

    def test_fixed_array_of_nullable_array(self):
        """Test fixed_array with nullable array elements."""
        desc = fixed_array(nullable(array(int, ","), "_"), "|")
        assert_conversions(desc, ([1, 2], None, [3]), "1,2|_|3")


class TestUniqueArray:
    """Tests for the unique_array factory method."""

    def test_unique_array_str(self):
        """Test unique_array of strings with ordering key."""
        desc = unique_array(str, "|")
        assert_conversions(desc, set(), "")
        assert_conversions(desc, {"a"}, "a")
        assert_conversions(desc, {"b"}, "b")

    def test_unique_array_str_with_ordering(self):
        """Test unique_array of strings with ordering key."""
        desc = unique_array(str, "|", ordering_key=lambda x: x)
        assert_conversions(desc, set(), "")
        assert_conversions(desc, {"a", "b", "c"}, "a|b|c")

    def test_unique_array_int_with_ordering(self):
        """Test unique_array of ints with ordering key."""
        desc = unique_array(int, ",", ordering_key=lambda x: x)
        assert_conversions(desc, set(), "")
        assert_conversions(desc, {1, 2, 3}, "1,2,3")

    def test_unique_array_with_custom_empty_marker(self):
        """Test unique_array with custom empty marker."""
        desc = unique_array(str, "|", empty_marker="_", ordering_key=lambda x: x)
        assert_conversions(desc, set(), "_")

    def test_unique_array_removes_duplicates_on_deserialization(self):
        """Test that unique_array removes duplicates during deserialization."""
        desc = unique_array(str, "|", ordering_key=lambda x: x)
        assert_deserialization(desc, "a|b|c|a", {"a", "b", "c"})

    def test_unique_array_serialization_order(self):
        """Test that unique_array serializes in order when ordering_key is provided."""
        desc = unique_array(str, "|", ordering_key=lambda x: x)
        # Sets are unordered, but with ordering_key it should be consistent
        assert_serialization(desc, {"c", "a", "b"}, "a|b|c")

    def test_unique_array_of_nullable(self):
        """Test unique_array with nested nullable descriptor."""
        desc = unique_array(nullable(int, "_"), "|", ordering_key=lambda x: (x is None, x))
        assert_conversions(desc, set(), "")
        assert_conversions(desc, {1, None, 3}, "1|3|_")

    def test_unique_array_of_via(self):
        """Test unique_array with via descriptor elements."""
        desc = unique_array(
            via(deserialize=lambda s: int(s), serialize=lambda x: str(x)),
            "|",
            ordering_key=lambda x: x,
        )
        assert_deserialization(desc, "1|2|3|1", {1, 2, 3})
        assert_serialization(desc, {3, 1, 2}, "1|2|3")


class TestMapping:
    """Tests for the mapping factory method."""

    def test_mapping_str_int(self):
        """Test mapping with str:int."""
        desc = mapping(str, int, "|", "=")
        assert_conversions(desc, {}, "")
        assert_conversions(desc, {"a": 1}, "a=1")
        assert_deserialization_error(desc, "b=")
        assert_deserialization_error(desc, "z")

    def test_mapping_str_nullable_str_compact_pair(self):
        """Test mapping with str:Optional[str]."""
        desc = mapping(str, nullable(str), "|", "=", "_", None, True)
        assert_conversions(desc, {"": None}, "")
        assert_conversions(desc, {"a": None}, "a")
        assert_conversions(desc, {"a": "$"}, "a=$")

    def test_mapping_str_nullable_str_with_custom_marker_compact_pair(self):
        """Test mapping with str:Optional[str]."""
        desc = mapping(str, nullable(str, "_"), "|", "=", "_", None, True)
        assert_conversions(desc, {"": None}, "=_")
        assert_conversions(desc, {"a": ""}, "a")
        assert_conversions(desc, {"a": "$"}, "a=$")

    def test_mapping_str_int_compact_pair(self):
        """Test mapping with str:str and ordering key."""
        desc = mapping(str, str, "|", "=", "_", None, True)
        assert_conversions(desc, {"": ""}, "")
        assert_conversions(desc, {"a": ""}, "a")
        assert_conversions(desc, {"a": "$"}, "a=$")

    def test_mapping_str_str_with_ordering(self):
        """Test mapping with str:str and ordering key."""
        desc = mapping(str, str, "|", "=", ordering_key=lambda x: x[0])
        assert_conversions(desc, {}, "")
        assert_conversions(desc, {"a": "1", "b": "2", "c": "3"}, "a=1|b=2|c=3")

    def test_mapping_str_int_with_ordering(self):
        """Test mapping with str:int and ordering key."""
        desc = mapping(str, int, "|", "=", ordering_key=lambda x: x[0])
        assert_conversions(desc, {}, "")
        assert_conversions(desc, {"a": 1, "b": 2}, "a=1|b=2")

    def test_mapping_int_str_with_ordering(self):
        """Test mapping with int:str and ordering key."""
        desc = mapping(int, str, "|", "=", ordering_key=lambda x: x[0])
        assert_conversions(desc, {}, "")
        assert_conversions(desc, {1: "a", 2: "b"}, "1=a|2=b")

    def test_mapping_with_custom_empty_marker(self):
        """Test mapping with custom empty marker."""
        desc = mapping(str, str, "|", "=", empty_marker="_", ordering_key=lambda x: x[0])
        assert_conversions(desc, {}, "_")

    def test_mapping_with_compact_pair(self):
        """Test mapping with use_compact_pair for empty values."""
        desc = mapping(str, str, "|", "=", use_compact_pair=True, ordering_key=lambda x: x[0])
        assert_conversions(desc, {"a": "", "b": "value"}, "a|b=value")

    def test_mapping_without_compact_pair_error(self):
        """Test that deserialization fails without use_compact_pair when no delimiter."""
        desc = mapping(str, str, "|", "=", use_compact_pair=False)
        assert_deserialization_error(desc, "a|b=value")

    def test_mapping_with_array_values(self):
        """Test mapping with array values."""
        desc = mapping(str, array(int, ","), "|", ":", ordering_key=lambda x: x[0])
        assert_conversions(desc, {}, "")
        assert_conversions(desc, {"a": [1, 2], "b": [3, 4]}, "a:1,2|b:3,4")

    def test_mapping_with_nullable_values(self):
        """Test mapping with nullable values."""
        desc = mapping(str, nullable(int, "_"), "|", "=", ordering_key=lambda x: x[0])
        assert_conversions(desc, {"a": 1, "b": None}, "a=1|b=_")

    def test_mapping_with_nested_mappings(self):
        """Test mapping with nested mapping values."""
        desc = mapping(
            str,
            mapping(str, int, ",", ":", ordering_key=lambda x: x[0]),
            "|",
            "=",
            ordering_key=lambda x: x[0],
        )
        assert_conversions(desc, {"a": {"x": 1, "y": 2}}, "a=x:1,y:2")


class TestVia:
    """Tests for the via factory method."""

    def test_via_simple_conversion(self):
        """Test via with simple conversion functions."""
        desc = via(deserialize=lambda s: int(s) * 2, serialize=lambda x: str(x // 2))
        assert_conversions(desc, 10, "5")

    def test_via_complex_type(self):
        """Test via with a complex type."""

        def parse_coords(s):
            x, y = s.split(",")
            return (float(x), float(y))

        def format_coords(coords):
            return f"{coords[0]},{coords[1]}"

        desc = via(deserialize=parse_coords, serialize=format_coords)
        assert_conversions(desc, (1.5, 2.5), "1.5,2.5")

    def test_via_with_stateful_functions(self):
        """Test via with functions that have state."""
        prefix = "PREFIX_"

        desc = via(deserialize=lambda s: prefix + s, serialize=lambda s: s.removeprefix(prefix))
        assert_conversions(desc, "PREFIX_value", "value")

    def test_via_nested_in_array(self):
        """Test via descriptor nested in an array descriptor."""
        desc = array(via(deserialize=lambda s: int(s) * 2, serialize=lambda x: str(x // 2)), "|")
        assert_conversions(desc, [2, 4, 6], "1|2|3")
