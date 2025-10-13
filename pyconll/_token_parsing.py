"""
Temporary module containing token parsing helper functions.

This module will be used during the refactoring process to separate parsing
logic from data structures. These functions parse the individual fields of
CoNLL-U token lines.
"""

from typing import Callable, Optional

from pyconll.exception import ParseError
from pyconll.unit.token import Token


def _unit_empty_map(value, empty):
    """
    Map unit values for CoNLL-U columns to a string or None if empty.

    Args:
        value: The value to map.
        empty: The empty representation for this unit.

    Returns:
        None if value is empty and value otherwise.
    """
    return None if value == empty else value


def _dict_empty_map_parser(v, v_delimiter):
    """
    Map a value into the appropriate form, for a standard dict based column.

    Args:
        v: The raw string value that was parsed from the column as a value.
        v_delimiter: The delimiter between components of the value.

    Returns:
        The parsed value, as a set of its components.

    Raises:
        ParseError: If there was an error parsing the value. This happens when
            the value is None.
    """
    if v is not None:
        vs = set(v.split(v_delimiter))
        return vs

    error_msg = f'Error parsing "{v}" properly. Please check against CoNLL format spec.'
    raise ParseError(error_msg)


def _dict_empty_map(values, empty, delim, av_separator, v_delimiter):
    """
    Map dict values for CoNLL-U columns to a dict or empty dict if empty.

    Args:
        values: The value to check for existence.
        empty: The empty representation for this dict.
        delim: The delimiter between components in the provided value.
        av_separator: The attribute-value separator for each component.
        v_delimiter: The delimiter between values for the same attribute.

    Returns:
        An empty dict if value is empty. Otherwise, a dict of key-value where
        the values are sets.

    Raises:
        ParseError: If the dict format was unable to parsed, because of a lack
            of a value.
    """
    return _dict_empty_map_helper(
        values, empty, delim, av_separator, v_delimiter, _dict_empty_map_parser
    )


def _create_dict_tupled_empty_parse(size, strict):
    """
    Parameterized creation of a parser for tupled values.

    Args:
        size: The expected size of the tuple.
        strict: Flag to signify if parsed values with less components than size
            will be accepted. In this case, missing values will be supplated
            with None.

    Returns:
        The parameterized parser function for parsing tupled columns.

    Raises:
        ParseError: If the parsing is strict and there is a component size
            mismatch, or if there are too many components in general.
    """

    def _dict_tupled_empty_parser(v, v_delimiter):
        """
        Map a value into the appropriate form, for a tupled based column.

        Args:
            v: The raw string value parsed from a column.
            v_delimiter: The delimiter between components of the value.

        Returns:
            The parsed value as a tuple.

        Raises:
            ParseError: If there was an error parsing the value as a tuple.
        """
        if v is None:
            raise ParseError(
                f'Error parsing "{v}" as tuple properly. Please check against the format spec.'
            )

        components = v.split(v_delimiter)
        left = size - len(components)

        if not strict and 0 <= left < size:
            vs = tuple(components + [None] * left)
        else:
            raise ParseError(
                f'Error parsing "{v}" as tuple properly. Please check against the format spec.'
            )

        return vs

    return _dict_tupled_empty_parser


TUPLE_PARSER_MEMOIZE: dict[int, Callable[[str, str], tuple[Optional[str], ...]]] = {}


def _dict_tupled_empty_map(values, empty, delim, av_separator, v_delimiter, size):
    """
    Map dict based values for CoNLL-U columns to a dict with tupled values.

    Tupled values are those with a maximum number of components, which is also
    greater than 1.

    Args:
        values: The value to parse.
        empty: The empty representation for this value in CoNLL format.
        delim: The delimiter between components in the value.
        av_separator: The separator between the attribute and value in each
            component.
        v_delimiter: The delimiter between values for the same attribute.
        size: The maximum size of the tuple. Components with less values than
            this will be supplanted with None.

    Returns:
        An empty dict if values was empty. Otherwise, a dictionary with fixed
        length tuples as the values.

    Raises:
        ParseError: If there was an error parsing the tuple. Related to the
            number of components.
    """
    try:
        parser = TUPLE_PARSER_MEMOIZE[size]
    except KeyError:
        parser = _create_dict_tupled_empty_parse(size, False)
        TUPLE_PARSER_MEMOIZE[size] = parser

    return _dict_empty_map_helper(values, empty, delim, av_separator, v_delimiter, parser)


def _dict_mixed_empty_parser(v, v_delimiter):
    """
    Parse a value into the appropriate form, for a mixed value based column.

    Args:
        v: The raw string value parsed from a column.
        v_delimiter: The delimiter between components of the value.

    Returns:
        The parsed value, which can either be None in the case of no
        corresponding value, or a set of the components in the value.
    """
    if v is None:
        return v

    vs = set(v.split(v_delimiter))
    return vs


def _dict_mixed_empty_map(values, empty, delim, av_separator, v_delimiter):
    """
    Map dict based values for CoNLL-U columns to dict with mixed values.

    Mixed values are those that can be either singletons or sets.

    Args:
        values: The value to parse.
        empty: The empty representation for this value in CoNLL-U format.
        delim: The delimiter between components in the value.
        av_separator: The separator between attribute and value in each
            component.
        v_delimiter: The delimiter between values for the same attribute.

    Returns:
        An empty dict if values is empty. Otherwise, a dictionary with either
        None, or a set of strings as the values.

    Raises:
        ParseError: If the dict format was unable to parsed.
    """
    return _dict_empty_map_helper(
        values, empty, delim, av_separator, v_delimiter, _dict_mixed_empty_parser
    )


def _dict_empty_map_helper(values, empty, delim, av_separator, v_delimiter, parser):
    """
    A helper to consolidate logic between singleton and non-singleton mapping.

    Args:
        values: The value to parse.
        empty: The empty representation for this value in CoNLL-U format.
        delim: The delimiter between components of the value.
        av_separator: The separator between attribute and value in each
            component.
        v_delimiter: The delimiter between values for the same attribute.
        parser: The parser of the value from the attribute value pair.

    Returns:
        An empty dict if the value is empty and otherwise a parsed equivalent.

    Raises:
        ParseError: If the dict format was unable to parsed. This error will be
            raised by the provided parser.
    """
    if values == empty:
        return {}

    d = {}
    for el in values.split(delim):
        parts = el.split(av_separator, 1)
        if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
            k = parts[0]
            v = None
        else:
            k, v = parts

        parsed = parser(v, v_delimiter)
        d[k] = parsed

    return d


def _parse_token(line: str, empty: bool = False) -> Token:
    """
    Parse a line into an in-memory representation of a Token.

    Args:
        line: The line to parse into a Token (expected to be typical CoNLL-U format).
        empty: Flag to control how empty forms and lemmas are parsed.

    Returns:
        The parsed Token from the line.

    Raises:
        ParseError: If there was an error parsing the token.
    """
    # Split the line into fields
    fields = line.split("\t")

    if len(fields) != 10:
        error_msg = f"The number of columns per token line must be 10. Invalid token: {line!r}"
        raise ParseError(error_msg)

    # Strip trailing newline if present
    if fields[-1][-1] == "\n":
        fields[-1] = fields[-1][:-1]

    # Parse fields with empty flag set to False
    token_id = fields[0]

    # Handle form and lemma with empty flag logic
    if empty or (fields[1] != "_" or fields[2] != "_"):
        form = _unit_empty_map(fields[1], "_")
        lemma = _unit_empty_map(fields[2], "_")
    else:
        form = fields[1]
        lemma = fields[2]

    upos = _unit_empty_map(fields[3], "_")
    xpos = _unit_empty_map(fields[4], "_")
    feats = _dict_empty_map(fields[5], "_", "|", "=", ",")
    head = _unit_empty_map(fields[6], "_")
    deprel = _unit_empty_map(fields[7], "_")
    deps = _dict_tupled_empty_map(fields[8], "_", "|", ":", ":", 4)
    misc = _dict_mixed_empty_map(fields[9], "_", "|", "=", ",")

    return Token(token_id, form, lemma, upos, xpos, feats, head, deprel, deps, misc)
