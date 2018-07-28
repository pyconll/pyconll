import operator

from pyconll.exception import ParseError


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
        ParseError: If the dict format was unable to parsed.
    """
    return _dict_empty_map_helper(values, empty, delim, av_separator,
                                  v_delimiter, False, False)


def _dict_singleton_empty_map(values, empty, delim, av_separator):
    """
    Map dict based values for CoNLL-U columns to dict with singleton values.

    Args:
        values: The value to parse.
        empty: The empty representation for this value in CoNLL-U format.
        delim: The delimiter between components in the value.
        av_separator: The separator between attribute and value in each
            component.

    Returns:
        An empty dict if values is empty. Otherwise, a dict of key-value pairs
        where the values are singletons.

    Raises:
        ParseError: If the dict format was unable to parsed.
    """
    return _dict_empty_map_helper(values, empty, delim, av_separator, None,
                                  True, False)


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

    Raises:
        ParseError: If the dict format was unable to parsed.
    """
    return _dict_empty_map_helper(values, empty, delim, av_separator,
                                  v_delimiter, False, True)


def _dict_empty_map_helper(values, empty, delim, av_separator, v_delimiter,
                           singleton, mixed):
    """
    A helper to consolidate logic between singleton and non-singleton mapping.

    Args:
        values: The value to parse.
        empty: The empty representation for this value in CoNLL-U format.
        delim: The delimiter between components of the value.
        av_separator: The separator between attribute and value in each
            component.
        v_delimiter: The delimiter between values for the same attribute.
        singleton: A flag to indicate if the value has singleton values or not.

    Returns:
        An empty dict if the value is empty and otherwise a parsed equivalent.

    Raises:
        ParseError: If the dict format was unable to parsed.
    """
    if values == empty:
        return {}
    else:
        d = {}
        for el in values.split(delim):
            parts = el.split(av_separator)
            if len(parts) == 1:
                k = parts[0]
                v = None
            elif len(parts) == 2:
                k, v = parts

            if (singleton and v is not None) or (mixed and v is None):
                d[k] = v
            elif (not singleton and not mixed and v is not None) or mixed:
                vs = set(v.split(v_delimiter))
                d[k] = vs
            else:
                error_msg = 'Error parsing {} properly. Please check against CoNLL format spec.'.format(values)
                raise ParseError(error_msg)

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


def _dict_conll_map(values, empty, delim, av_separator, v_delimiter):
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

    Returns:
        The CoNLL-U format as a string.
    """
    return _dict_conll_map_helper(values, empty, delim, av_separator,
                                  v_delimiter, False, False)


def _dict_singleton_conll_map(values, empty, delim, av_separator):
    """
    Map a dict whose attributes can only have one value to CoNLL-U format.

    Args:
        values: The dict to convert to CoNLL-U format.
        empty: The empty CoNLL-U representation for this value.
        delim: The delimiter between attribute-value pairs.
        av_separator: The separator between attribute and value.

    Returns:
        The CoNLL-U formatted equivalent to the value.
    """
    return _dict_conll_map_helper(values, empty, delim, av_separator, None,
                                  True, False)


def _dict_mixed_conll_map(values, empty, delim, av_separator, v_delimiter):
    """
    Map a dict whose components can be mixed to a CoNLL-U format.

    Args:
        values: The dict to convert to CoNLL-U format.
        empty: The empty CoNLL-U representation for this value.
        delim: The delimiter between attribute-value pairs.
        av_separator: The separator between attribute and value.
        v_delimiter: The delimiter between values of the same attribute if
            necessary.

    Returns:
        The CoNLL-U formatted equivalent to the value.
    """
    return _dict_conll_map_helper(values, empty, delim, av_separator,
                                  v_delimiter, False, True)


def _dict_conll_map_helper(values, empty, delim, av_separator, v_delimiter,
                           singleton, mixed):
    """
    Helper to map dicts to CoNLL-U format equivalents.

    Args:
        values: The value, dict, to map.
        empty: The empty CoNLL-U reprsentation for this value.
        delim: The delimiter between attribute-value pairs.
        av_separator: The separator between attribute and value.
        v_delimiter: The delimiter between values of the same attribute if
            necessary.
        singleton: Flag to indicate if the dictionary values are singletons or
            collections.

    Returns:
        The CoNLL-U formatted equivalent to the value.
    """
    if values == {}:
        return empty
    else:
        sorted_av_pairs = sorted(values.items(), key=operator.itemgetter(0))

        if singleton:
            av_pairs = sorted_av_pairs
        else:
            av_pairs = []
            for pair in sorted_av_pairs:
                if mixed and pair[1] is None:
                    av_pairs.append([pair[0]])
                else:
                    sorted_attr_values = sorted(pair[1], key=str.lower)
                    str_attrs = v_delimiter.join(sorted_attr_values)

                    av_pairs.append([pair[0], str_attrs])

        return delim.join([av_separator.join(pair) for pair in av_pairs])


class Token:
    # TODO: Allow custom, token parsing for misc field if necessary somehow.
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

    # The different delimiters and separators for the CoNLL-U format.
    # FIELD_DELIMITER separates columns on the token line.
    # COMPONENT_DELIMITER separates a field with multiple components.
    # AV_SEPARATOR separates the attribute from the value in a component.
    # V_DELIMITER separates the values in an attribute-value pair.
    FIELD_DELIMITER = '\t'
    COMPONENT_DELIMITER = '|'
    AV_SEPARATOR = '='
    AV_DEPS_SEPARATOR = ':'
    V_DELIMITER = ','
    EMPTY = '_'

    def __init__(self, source, empty=True, _line_number=None):
        """
        Construct the token from the given source.

        A Token line must end in an an LF line break according to the
        specification. However, this method will accept a line with or without
        this ending line break.

        Further, a '_' that appears in the form and lemma is ambiguous and can
        either refer to an empty value or an actual underscore. So the flag
        empty_form allows for control over this if it is known from outside
        information. If, the token is a multiword token, all fields except for
        form should be empty.

        Note that no validation is done on input. Valid input will be processed
        properly, but there is no guarantee as to invalid input that does not
        follow the CoNLL-U specifications.

        Args:
            line: The line that represents the Token in CoNLL-U format.
            empty: A flag to signify if the word form and lemma can be assumed
                to be empty and not the token signifying empty. Only if both the
                form and lemma are both the same token as empty and there is no
                empty assumption, will they not be assigned to None.
            _line_number: The line number for this Token in a CoNLL-U file. For
                internal use mostly.

        Raises:
            ParseError: If the provided source is not composed of 10 tab
                separated columns.
        """
        if source[-1] == '\n':
            source = source[:-1]
        self._source = source

        self.line_number = _line_number

        fields = source.split(Token.FIELD_DELIMITER)
        self._fields = fields

        if len(self._fields) != 10:
            error_msg = 'The number of columns per token line must be 10. Invalid token: {}'.format(
                source)
            raise ParseError(error_msg)

        # Assign all the field values from the line to internal equivalents.
        self.id = fields[0]

        # If we can assume the form and lemma are empty, or if either of the
        # fields are not the empty token, then we can proceed as usual.
        # Otherwise, these empty tokens might not mean empty, but rather the
        # actual tokens.
        if empty or (fields[1] != Token.EMPTY or fields[2] != Token.EMPTY):
            self._form = _unit_empty_map(fields[1], Token.EMPTY)
            self.lemma = _unit_empty_map(fields[2], Token.EMPTY)
        elif fields[1] == Token.EMPTY and fields[2] == Token.EMPTY:
            self._form = fields[1]
            self.lemma = fields[2]

        self.upos = _unit_empty_map(fields[3], Token.EMPTY)
        self.xpos = _unit_empty_map(fields[4], Token.EMPTY)
        self.feats = _dict_empty_map(fields[5], Token.EMPTY,
                                     Token.COMPONENT_DELIMITER,
                                     Token.AV_SEPARATOR, Token.V_DELIMITER)
        self.head = _unit_empty_map(fields[6], Token.EMPTY)
        self.deprel = _unit_empty_map(fields[7], Token.EMPTY)
        self.deps = _dict_singleton_empty_map(fields[8], Token.EMPTY,
                                              Token.COMPONENT_DELIMITER,
                                              Token.AV_DEPS_SEPARATOR)
        # TODO: Handle misc field better. I'm not sure if it has to be key-value
        # structure.
        self.misc = _dict_mixed_empty_map(
            fields[9], Token.EMPTY, Token.COMPONENT_DELIMITER,
            Token.AV_SEPARATOR, Token.V_DELIMITER)

    @property
    def form(self):
        """
        Provide the word form of this Token. This property makes it readonly.

        Returns:
            The Token wordform.
        """
        return self._form

    def is_multiword(self):
        """
        Checks if this token is a multiword token.

        Returns:
            True if this token is a multiword token, and False otherwise.
        """
        return '-' in self.id

    def conll(self):
        """
        Convert Token to the CoNLL-U representation.

        Note that this does not include a newline at the end.

        Returns:
            A string representing the token as a line in a CoNLL-U file.
        """
        # Transform the internal CoNLL-U representations back to text and
        # combine the fields.
        id = self.id
        form = _unit_conll_map(self.form, Token.EMPTY)
        lemma = _unit_conll_map(self.lemma, Token.EMPTY)
        upos = _unit_conll_map(self.upos, Token.EMPTY)
        xpos = _unit_conll_map(self.xpos, Token.EMPTY)
        feats = _dict_conll_map(self.feats, Token.EMPTY,
                                Token.COMPONENT_DELIMITER, Token.AV_SEPARATOR,
                                Token.V_DELIMITER)
        head = _unit_conll_map(self.head, Token.EMPTY)
        deprel = _unit_conll_map(self.deprel, Token.EMPTY)
        deps = _dict_singleton_conll_map(self.deps, Token.EMPTY,
                                         Token.COMPONENT_DELIMITER,
                                         Token.AV_DEPS_SEPARATOR)
        misc = _dict_mixed_conll_map(self.misc, Token.EMPTY,
                                     Token.COMPONENT_DELIMITER,
                                     Token.AV_SEPARATOR, Token.V_DELIMITER)

        items = [id, form, lemma, upos, xpos, feats, head, deprel, deps, misc]

        return Token.FIELD_DELIMITER.join(items)

    def __eq__(self, other):
        """
        Test if this Token is equal to other.

        Args:
            other: The other token to compare against.

        Returns:
            True if the this Token and the other are the same. Two tokens are
            considered the same when all columns are the same.
        """
        return self._source == other._source
