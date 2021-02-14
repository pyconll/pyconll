"""
Defines the Token type and parsing and output logic. A Token is the based unit
in CoNLL-U and so the data and parsing in this module is central to the CoNLL-U
format.
"""

import functools
import math
from typing import Callable, ClassVar, Dict, Optional, Set, Tuple

from pyconll.conllable import Conllable
from pyconll.exception import ParseError, FormatError


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

    error_msg = 'Error parsing "{}" properly. Please check against CoNLL format spec.'.format(
        v)
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
    return _dict_empty_map_helper(values, empty, delim, av_separator,
                                  v_delimiter, _dict_empty_map_parser)


def _create_dict_tupled_empty_parse(size, strict):
    """
    Parameterized creation of a parser for tupled values.

    Args:
        size: The expected size of the tuple.
        strict: Flag to signifiy if parsed values with less components than size
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
            error_msg = ('Error parsing "{}" as tuple properly. Please check'
                         'against CoNLL format spec').format(v)
            raise ParseError(error_msg)

        components = v.split(v_delimiter)
        left = size - len(components)

        if not strict and 0 <= left < size:
            vs = tuple(components + [None] * left)
        else:
            error_msg = ('Error parsing "{}" as tuple properly. Please'
                         'check against CoNLL format spec.').format(v)
            raise ParseError(error_msg)

        return vs

    return _dict_tupled_empty_parser


TUPLE_PARSER_MEMOIZE: Dict[int, Callable[[str, str], Tuple[Optional[str],
                                                           ...]]] = {}


def _dict_tupled_empty_map(values, empty, delim, av_separator, v_delimiter,
                           size):
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

    return _dict_empty_map_helper(values, empty, delim, av_separator,
                                  v_delimiter, parser)


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
    return _dict_empty_map_helper(values, empty, delim, av_separator,
                                  v_delimiter, _dict_mixed_empty_parser)


def _dict_empty_map_helper(values, empty, delim, av_separator, v_delimiter,
                           parser):
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
        if len(parts) == 1 or (len(parts) == 2 and parts[1] == ''):
            k = parts[0]
            v = None
        elif len(parts) == 2:
            k, v = parts

        parsed = parser(v, v_delimiter)
        d[k] = parsed

    return d


def _unit_conll_map(value, empty):
    """
    Map a unit value to its CoNLL-U format equivalent.

    Args:
        value: The value to convert to its CoNLL-U format.
        empty: The empty representation for a unit in CoNLL-U.

    Returns:
        empty if value is None and value otherwise.
    """
    return empty if value is None else value


def _dict_conll_map_formatter(v, v_delimiter):
    """
    Formatter to convert a set of CoNLL values to a string representation.

    Args:
        v: The set of values.
        v_delimiter: The delimiter between the values in a string representation.

    Returns:
        The appropriate string representation of the value in CoNLL format.

    Raises:
        FormatError: When there are no values to output.
    """
    if v:
        sorted_vs = sorted(v, key=str.lower)
        str_vs = v_delimiter.join(sorted_vs)
    else:
        error_msg = 'There are no values to format.'
        raise FormatError(error_msg)

    return str_vs


def _dict_conll_map(values, empty, delim, av_separator, v_delimiter, av_key):
    """
    Map a dict whose attributes can have multiple values to CoNLL-U format.

    This CoNLL-U format will be sorted alphabetically by attribute and
    attributes with more than one value will have values sorted
    alphabetically.

    Args:
        values: The dict to convert to its CoNLL-U format.
        empty: The empty representation for a dict in CoNLL-U.
        delim: The delimiter between components in the output.
        av_separator: The attribute-value separator in the provided string.
        v_delimiter: The delimiter between values in attribute-value pairs.
        av_key: The key for attribute-value pairs ordering, on output.

    Returns:
        The CoNLL-U format as a string.
    """
    return _dict_conll_map_helper(values, empty, delim, av_separator,
                                  v_delimiter, _dict_conll_map_formatter,
                                  av_key)


def _dict_tupled_conll_formatter(v, v_delimiter):
    """
    Convert a tuple of values into a CoNLL string representation.

    Args:
        v: The tuple of values to convert.
        v_delimiter: The delimiter between values in the ConLL representation.

    Returns:
        The string representation of the tuple in CoNLL format.

    Raises:
        FormatError: When all values in the tuple value are None.
    """
    presents = list(filter(lambda el: el is not None, v))
    if not presents:
        error_msg = 'All values in the tuple are None.'
        raise FormatError(error_msg)

    form = v_delimiter.join(presents)
    return form


def _dict_tupled_conll_map(values, empty, delim, av_separator, v_delimiter,
                           av_key):
    """
    Map a dict whose components are max length tuples to a CoNLL format.

    Args:
        values: The dict to convert.
        empty: The empty CoNLL representation for this value.
        delim: The delimiter between attribute-value pairs.
        av_separator: The separator between the attribute and value.
        v_delimiter: The delimiter between values of the same attribute.
        av_key: The ordering for the attribute-value pairs, on output.

    Returns:
        The CoNLL formatted equivalent to the provided value as a tupled column.

    Raises:
        FormatError: If there was an error converting a tuple to a CoNLL format.
    """
    return _dict_conll_map_helper(values, empty, delim, av_separator,
                                  v_delimiter, _dict_tupled_conll_formatter,
                                  av_key)


def _dict_mixed_conll_formatter(v, v_delimiter):
    """
    Format a mixed value into a string representation.

    Args:
        v: The value to convert to a mixed CoNLL string format.
        v_delimiter: The delimiter between values in the string.

    Returns:
        A CoNLL representation of the mixed value.
    """
    if v is None:
        return v

    sorted_vs = sorted(v, key=str.lower)
    str_vs = v_delimiter.join(sorted_vs)

    return str_vs


def _dict_mixed_conll_map(values, empty, delim, av_separator, v_delimiter,
                          av_key):
    """
    Map a dict whose components can be mixed to a CoNLL-U format.

    Args:
        values: The dict to convert to CoNLL-U format.
        empty: The empty CoNLL-U representation for this value.
        delim: The delimiter between attribute-value pairs.
        av_separator: The separator between attribute and value.
        v_delimiter: The delimiter between values of the same attribute if
            necessary.
        av_key: The ordering for the attribute-value pairs, on output.

    Returns:
        The CoNLL-U formatted equivalent to the value.
    """
    return _dict_conll_map_helper(values, empty, delim, av_separator,
                                  v_delimiter, _dict_mixed_conll_formatter,
                                  av_key)


def _dict_conll_map_helper(values, empty, delim, av_separator, v_delimiter,
                           formatter, av_key):
    """
    Helper to map dicts to CoNLL-U format equivalents.

    Args:
        values: The value, dict, to map.
        empty: The empty CoNLL-U representation for this value.
        delim: The delimiter between attribute-value pairs.
        av_separator: The separator between attribute and value.
        v_delimiter: The delimiter between values of the same attribute if
            necessary.
        formatter: The function to convert an attribute value pair into a CoNLL
            column representation. This function should take in a value
            representation, and a value delimiter, and output a string
            representation. It should also output None to mean there is no
            string representation.
        av_key: The sorting key for the attribute-value pairs on output.

    Returns:
        The CoNLL-U formatted equivalent to the value.
    """
    def paramed(pair):
        f = formatter(pair[1], v_delimiter)
        if f is None:
            return (pair[0], )

        return (pair[0], f)

    if values == {}:
        return empty

    sorted_av_pairs = sorted(values.items(), key=av_key)
    formatted = map(paramed, sorted_av_pairs)
    output = delim.join([av_separator.join(form) for form in formatted])

    return output if output else empty


@functools.total_ordering
class _TokenIdComparer:
    """
    Implementation class for comparing token ids to be sorted, using the
    standard python sorting routines. Two ids are equal if the id text is
    exactly the same. Otherwise, ids are compared by parts, with a range id
    being compared by the start index and then by the end index, and decimal
    ids having the radix separated parts compared separately.
    """
    def __init__(self, token_id):
        """
        Create the comparer wrapping the given, assumed valid format, id.

        Args:
            token_id: The token id to wrap.
        """
        self.token_id = token_id

    def __eq__(self, other):
        """
        Compares if the current id is equal to the provided id.

        Args:
            other: The other id wrapper to compare against.

        Returns:
            True if the two underlying ids are exactly the same.
        """
        return self.token_id == other.token_id

    def __ne__(self, other):
        """
        Compares if the current id is not equal to the provided id.

        Args:
            other: The other id wrapper to compare against.

        Returns:
            True if the two underlying ids are not the same.
        """
        return not self == other

    @staticmethod
    def _split_token_id_as_range(token_id):
        """
        Splits a token into its individual parts as a range.

        If the token does not represent a range, the beginning and end are the
        same token id.

        Args:
            token_id: The id to split into its range parts.

        Returns:
            A tuple of size two with the token id representing the range.
        """
        idx = token_id.find('-')
        if idx < 0:
            ranges = (token_id, token_id)
        else:
            ranges = (token_id[:idx], token_id[idx + 1:])

        return ranges

    @staticmethod
    def _split_by_radix(token_id):
        """
        Split a non-range token id by the radix point.

        Any id without a radix point will assume it is 0.

        Args:
            token_id: The id to decompose into its two parts based on the radix.

        Returns:
            A tuple of size 2 with the id parts decomposed as integers.
        """
        idx = token_id.find('.')
        if idx < 0:
            return [int(token_id), 0]

        first = int(token_id[:idx])
        second = int(token_id[idx + 1:])
        return [first, second]

    @staticmethod
    def _cmp_individual_ids(a, b):
        """
        Compare two non-range token ids using a traditional compare function.

        Args:
            a: The first argument to compare and the basis of the comparison.
            b: The second argument to compare against.

        Returns:
            The results of a traditional compare function in basis of a to b.
        """
        a_l, a_r = _TokenIdComparer._split_by_radix(a)
        b_l, b_r = _TokenIdComparer._split_by_radix(b)

        return _TokenIdComparer._zcopysign(2, a_l - b_l) + \
               _TokenIdComparer._zcopysign(1, a_r - b_r)

    @staticmethod
    def _zcopysign(a, b):
        """
        copysign that returns the sign indicator if it is 0 or -0.

        Args:
            a: The magnitude.
            b: The sign indicator.

        Returns:
            Usual copysign result unless sign indicator is 0.
        """
        if not b:
            return b

        return math.copysign(a, b)

    def __lt__(self, other):
        """
        Compares if other is less than the currently wrapped id.

        Args:
            other: The wrapped id to compare against.

        Returns:
            True if the current id is less than the id wrapped by other.
        """
        self_split_1, self_split_2 = _TokenIdComparer._split_token_id_as_range(
            self.token_id)
        other_split_1, other_split_2 = _TokenIdComparer._split_token_id_as_range(
            other.token_id)

        first_cmp = _TokenIdComparer._cmp_individual_ids(
            self_split_1, other_split_1)

        return first_cmp < 0 or (first_cmp == 0
                                 and _TokenIdComparer._cmp_individual_ids(
                                     self_split_2, other_split_2))


class Token(Conllable):
    """
    A token in a CoNLL-U file. This consists of 10 columns, each separated by
    a single tab character and ending in an LF ('\\n') line break. Each of the 10
    column values corresponds to a specific component of the token, such as id,
    word form, lemma, etc.

    This class does not do any formatting validation on input or output. This
    means that invalid input may be properly processed and then output. Or that
    client changes to the token may result in invalid data that can then be
    output. Properly formatted CoNLL-U will always work on input and as long as
    all basic units are strings output will work as expected. The result may
    just not be proper CoNLL-U.

    Also note that the word form for a token is immutable. This is because
    CoNLL-U is inherently interested in annotation schemes and not storing
    sentences.
    """

    __slots__ = [
        'id', '_form', 'lemma', 'upos', 'xpos', 'feats', 'head', 'deprel',
        'deps', 'misc'
    ]

    # The different delimiters and separators for the CoNLL-U format.
    # FIELD_DELIMITER separates columns on the token line.
    # COMPONENT_DELIMITER separates a field with multiple components.
    # AV_SEPARATOR separates the attribute from the value in a component.
    # V_DELIMITER separates the values in an attribute-value pair.
    FIELD_DELIMITER: ClassVar[str] = '\t'
    COMPONENT_DELIMITER: ClassVar[str] = '|'
    AV_SEPARATOR: ClassVar[str] = '='
    AV_DEPS_SEPARATOR: ClassVar[str] = ':'
    V_DELIMITER: ClassVar[str] = ','
    V_DEPS_DELIMITER: ClassVar[str] = ':'
    EMPTY: ClassVar[str] = '_'

    # Keys for sorting attribute-value columns. BY_ID converts the attribute
    # value pair to the integer value of the attribute, and BY_CASE_SENSITIVE
    # converts the pair to the lowercase version of the attribute.
    BY_ID: ClassVar[Callable[[Tuple[
        str, str]], _TokenIdComparer]] = lambda pair: _TokenIdComparer(pair[0])
    BY_CASE_INSENSITIVE: ClassVar[Callable[[Tuple[
        str, str]], str]] = lambda pair: pair[0].lower()

    def __init__(self, source: str, empty: bool = False) -> None:
        """
        Construct a Token from the given source line.

        A Token line ends in an an LF line break according to the CoNLL-U
        specification. However, this method accepts a line with or without the
        LF line break.

        On parsing, a '_' in the form and lemma is ambiguous and either refers
        to an empty value or to an actual underscore. The empty parameter flag
        controls how this situation should be handled.

        This method also guarantees properly processing valid input, but invalid
        input may not be parsed properly. Some inputs that do not follow the
        CoNLL-U specification may still be parsed properly and as expected. So
        proper parsing is not an indication of validity.

        Args:
            line: The line that represents the Token in CoNLL-U format.
            empty: A flag to control if the word form and lemma can be assumed
                to be empty and not the token signifying empty. If both the form
                and lemma are underscores and empty is set to False (there is no
                empty assumption), then the form and lemma will be underscores
                rather than None.

        Raises:
            ParseError: On various parsing errors, such as not enough columns or
                improper column values.
        """
        if source[-1] == '\n':
            source = source[:-1]

        fields = source.split(Token.FIELD_DELIMITER)

        if len(fields) != 10:
            error_msg = 'The number of columns per token line must be 10. Invalid token: {}'.format(
                source)
            raise ParseError(error_msg)

        # Assign all the field values from the line to internal equivalents.
        self.id: str = fields[0]

        # If we can assume the form and lemma are empty, or if either of the
        # fields are not the empty token, then we can proceed as usual.
        # Otherwise, these empty tokens might not mean empty, but rather the
        # actual tokens.
        if empty or (fields[1] != Token.EMPTY or fields[2] != Token.EMPTY):
            self._form: Optional[str] = _unit_empty_map(fields[1], Token.EMPTY)
            self.lemma: Optional[str] = _unit_empty_map(fields[2], Token.EMPTY)
        else:
            self._form = fields[1]
            self.lemma = fields[2]

        self.upos: Optional[str] = _unit_empty_map(fields[3], Token.EMPTY)
        self.xpos: Optional[str] = _unit_empty_map(fields[4], Token.EMPTY)
        self.feats: Dict[str,
                         Set[str]] = _dict_empty_map(fields[5], Token.EMPTY,
                                                     Token.COMPONENT_DELIMITER,
                                                     Token.AV_SEPARATOR,
                                                     Token.V_DELIMITER)
        self.head: Optional[str] = _unit_empty_map(fields[6], Token.EMPTY)
        self.deprel: Optional[str] = _unit_empty_map(fields[7], Token.EMPTY)
        self.deps: Dict[str,
                        Tuple[str, str, str, str]] = _dict_tupled_empty_map(
                            fields[8], Token.EMPTY, Token.COMPONENT_DELIMITER,
                            Token.AV_DEPS_SEPARATOR, Token.V_DEPS_DELIMITER, 4)
        self.misc: Dict[str, Optional[Set[str]]] = _dict_mixed_empty_map(
            fields[9], Token.EMPTY, Token.COMPONENT_DELIMITER,
            Token.AV_SEPARATOR, Token.V_DELIMITER)

    @property
    def form(self) -> Optional[str]:
        """
        Provide the word form of this Token. This property is read only.

        Returns:
            The Token form.
        """
        return self._form

    def is_multiword(self) -> bool:
        """
        Checks if this Token is a multiword token.

        Returns:
            True if this token is a multiword token, and False otherwise.
        """
        return '-' in self.id

    def conll(self) -> str:
        """
        Convert this Token to its CoNLL-U representation.

        A Token's CoNLL-U representation is a line. Note that this method does
        not include a newline at the end.

        Returns:
            A string representing the Token in CoNLL-U format.
        """
        # Transform the internal CoNLL-U representations back to text and
        # combine the fields.
        token_id = self.id
        form = _unit_conll_map(self.form, Token.EMPTY)
        lemma = _unit_conll_map(self.lemma, Token.EMPTY)
        upos = _unit_conll_map(self.upos, Token.EMPTY)
        xpos = _unit_conll_map(self.xpos, Token.EMPTY)
        feats = _dict_conll_map(self.feats, Token.EMPTY,
                                Token.COMPONENT_DELIMITER, Token.AV_SEPARATOR,
                                Token.V_DELIMITER, Token.BY_CASE_INSENSITIVE)
        head = _unit_conll_map(self.head, Token.EMPTY)
        deprel = _unit_conll_map(self.deprel, Token.EMPTY)
        deps = _dict_tupled_conll_map(self.deps, Token.EMPTY,
                                      Token.COMPONENT_DELIMITER,
                                      Token.AV_DEPS_SEPARATOR,
                                      Token.V_DEPS_DELIMITER, Token.BY_ID)
        misc = _dict_mixed_conll_map(self.misc, Token.EMPTY,
                                     Token.COMPONENT_DELIMITER,
                                     Token.AV_SEPARATOR, Token.V_DELIMITER,
                                     Token.BY_CASE_INSENSITIVE)

        items = [
            token_id, form, lemma, upos, xpos, feats, head, deprel, deps, misc
        ]

        return Token.FIELD_DELIMITER.join(items)
