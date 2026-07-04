"""Tests for internal IR code generation."""

from types import CodeType

import pytest

from pyconll._ir import process_ir


def test_process_ir_compiles_function():
    """
    Test that process_ir correctly strips indentation and compiles a function definition.
    """
    process_ir(t"""
        def add(a, b):
            return a + b
        """)


def test_process_ir_typed_interpolation():
    """
    Test that a typed tuple interpolation (value, type) is inlined when types match.
    """
    val = 99
    process_ir(t"x = {(val, int)}")


def test_process_ir_nested_template_interpolation():
    """
    Test that a nested Template value via the :t format spec is recursively interpolated.
    """
    body = t"return 1 + 1"
    process_ir(t"""
        def fn():
            {body:t}
        """)


def test_process_ir_all_empty_lines():
    """
    Test that a template consisting entirely of empty lines is handled without error.
    """
    process_ir(t"\n\n")


def test_process_ir_conversion_on_template_format_spec():
    """
    Test that combining a conversion flag with the :t format spec raises RuntimeError.
    """
    x = "test"
    with pytest.raises(RuntimeError, match="Cannot provide a conversion on a template value"):
        process_ir(t"{x!r:t}")


def test_process_ir_template_format_spec_requires_template_value():
    """
    Test that using the :t format spec with a non-Template value raises RuntimeError.
    """
    x = "not a template"
    with pytest.raises(RuntimeError, match="does not match the desired"):
        process_ir(t"{x:t}")


def test_process_ir_type_mismatch():
    """
    Test that an interpolation whose value type doesn't match the declared type raises RuntimeError.
    """
    with pytest.raises(RuntimeError, match="does not match the desired"):
        process_ir(t"{(42, str)}")


def test_process_ir_inconsistent_indentation_whitespace():
    """
    Test that IR code with mixed spaces and tabs in its leading indentation raises RuntimeError.
    """
    with pytest.raises(RuntimeError, match="Inconsistent whitespace"):
        process_ir(t"    \thello")


def test_process_ir_line_missing_expected_prefix():
    """
    Test that IR code where a subsequent line lacks the indentation prefix of the first raises
    RuntimeError.
    """
    with pytest.raises(RuntimeError, match="Expected whitespace prefix"):
        process_ir(t"    hello\n  world")
