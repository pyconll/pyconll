def _unit_empty_map(value, empty):
    """
    Map unit values for CoNLL-U columns that are empty to a value of None.

    Args:
    value: The value to check for existence. Should be a string.
    empty: The empty representation for this unit.

    Returns:
    None if value is empty and value otherwise.
    """
    return None if value == empty else value

def _dict_empty_map(values, empty, delim, av_separator, v_delimiter):
    """
    Map dict based values for CoNLL-U columns that are empty to an empty dict.

    Args:
    values: The value to check for existence. Should be a string.
    empty: The empty representation for this dict.
    delim: The delimiter between values in the provided string.
    av_separator: The attribute-value separator in the provided string.
    v_delimiter: The delimiter between values for the same attribute.

    Returns:
    An empty dict if value is empty. Otherwise, a dict of key-value pairs split
    on the Token feature delimiter.
    """
    if values == empty:
        return {}
    else:
        d = {}
        for el in values.split(delim):
            k, v = el.split(av_separator)
            v = set(v.split(v_delimiter))
            d[k] = v

        return d

def _list_empty_map(values, empty, delim):
    """
    Map list based values for CoNLL-U columns that are empty to an empty list.

    Args:
    values: The value to check for existence. Should be a string.
    empty: The empty representation for this list.
    delim: The delimiter between values in the provided string.

    Returns:
    An empty list if the value is empty and a list of the values otherwise.
    """
    return [] if values == empty else values.split(delim)

def _unit_conllu_map(value, empty):
    """
    Map a unit value to its CoNLL-U format equivalent.

    Args:
    value: The value to convert to its CoNLL-U format. Should be a string.
    empty: The empty representation for a unit in CoNLL-U.

    Returns:
    empty if value is None and value otherwise.
    """
    return empty if value is None else value

def _dict_conllu_map(values, empty, delim, av_separator, v_delimiter):
    """
    Map a dict based value to its CoNLL-U format equivalent.

    This CoNLL-U format will be sorted alphabetically by attribute.

    Args:
    values: The dict to convert to its CoNLL-U format.
    empty: The empty representation for a dict in CoNLL-U.
    delim: The delimiter between values in the output.
    av_separator: The attribute-value separator in the provided string.
    v_delimiter: The delimiter between values in attribute-value pairs.

    Returns:
    The CoNLL-U format as a string.
    """
    if values == {}:
        return empty
    else:
        sorted_d = sorted(values.items(), key=lambda k, v: k)
        for pair in sorted_d:
            pair[1] = sorted(pair[1], key=str.lower).join(v_delimiter)

        return \
            [pair.join(av_separator) for pair in sorted_d].join(delim)

def _list_conllu_map(values, empty, delim):
    """
    Map a list to its CoNLL-U format equivalent.

    Args:
    values: The list to convert to its CoNLL-U format.
    empty: The empty representation for a list in CoNLL-U.
    delim: The delimiter between the values of the list.

    Returns:
    The list in CoNLL-U format as a string.
    """
    return empty if values == [] else values.join(delim)


class Token:
    """
    A token in a CoNLL-U file. This consists of 10 columns, each separated by
    a single tab character and ending in an LF ('\n') line break. Each of the 10
    column values corresponds to a specific component of the token, such as id,
    word form, lemma, etc.
    """

    # The different delimiters and separators for the CoNLL-U format.
    # FIELD_DELIMITER separates columns on the token line.
    # COMPONENT_DELIMITER separates a field with multiple values.
    # AV_SEPARATOR separates the attribute from the value in a component.
    # V_DELIMITER separates the values in an attribute-value pair.
    FIELD_DELIMITER = '\t'
    COMPONENT_DELIMITER = '|'
    AV_SEPARATOR = '='
    V_DELIMITER = ','
    EMPTY = '_'

    def __init__(self, line, empty=True):
        """
        Construct the token from the given line.

        A Token line must end in an an LF line break according to the
        specification. However, this method will accept a line with or without
        this ending line break.

        Further, a '_' that appears in the form and lemma is ambiguous and can
        either refer to an empty value or an actual underscore. So the flag
        empty_form allows for control over this if it is known from outside
        information. If, the token is a multiword token, all fields except for
        form are empty.

        Note that no validation is done on input. Valid input will be processed
        properly, but there is no guarantee as to invalid input that does not
        follow the CoNLL-U specifications.

        Args:
        line: The line that represents the Token in CoNLL-U format.
        empty: A flag to signify if the word form and lemma can be assumed to be
            empty and not the token signifying empty.
        """
        if line[-1] == '\n':
            line = line[:-1]

        fields = line.split(Token.FIELD_DELIMITER)

        # Assign all the field values from the line to internal equivalents.
        self.id = fields[0]

        # If we can assume the form and lemma are empty, or if either of the
        # fields are not the empty token, then we can proceed as usual.
        # Otherwise, these empty tokens might not mean empty, but rather the
        # actual tokens.
        if empty or (fields[1] != Token.EMPTY or fields[2] != Token.EMPTY):
            self.form = _unit_empty_map(fields[1], Token.EMPTY)
            self.lemma = _unit_empty_map(fields[2], Token.EMPTY)
        elif fields[1] == Token.EMPTY and fields[2] == Token.EMPTY:
            self.form = fields[1]
            self.lemma = fields[2]

        self.upos = _unit_empty_map(fields[3], Token.EMPTY)
        self.xpos = _unit_empty_map(fields[4], Token.EMPTY)
        self.feats = _dict_empty_map(fields[5], Token.EMPTY,
            Token.COMPONENT_DELIMITER, Token.AV_SEPARATOR, Token.V_DELIMITER)
        self.head = _unit_empty_map(fields[6], Token.EMPTY)
        self.deprel = _unit_empty_map(fields[7], Token.EMPTY)
        self.deps = _dict_empty_map(fields[8], Token.EMPTY,
            Token.COMPONENT_DELIMITER, Token.AV_SEPARATOR, Token.V_DELIMITER)
        self.misc = _list_empty_map(fields[9], Token.EMPTY, Token.COMPONENT_DELIMITER)

    def is_multiword(self):
        """
        Checks if this token is a multiword token.

        Returns:
        True if this token is a multiword token, and False otherwise.
        """
        return '-' in self.id

    def __str__(self):
        """
        Convert to a string by providing the word form of the token.

        Returns:
        The word form of the token as a string representation.
        """
        return self.form

    def __repr__(self):
        """
        Convert Token to the CoNLL-U representation.

        Returns:
        A string representing the token as a line in a CoNLL-U file.
        """
        # Transform the internal CoNLL-U representations back to text and
        # combine the fields.
        id = self.id
        form = _unit_conllu_map(self.form)
        lemma = _unit_conllu_map(self.lemma)
        upos = _unit_conllu_map(self.upos)
        xpos = _unit_conllu_map(self.xpos)
        feats = _dict_conllu_map(self.feats, Token.COMPONENT_DELIMITER,
            Token.AV_SEPARATOR, Token.V_DELIMITER)
        head = _unit_conllu_map(self.head)
        deprel = _unit_conllu_map(self.deprel)
        deps = _dict_conllu_map(self.deps, Token.COMPONENT_DELIMITER,
            Token.AV_SEPARATOR, Token.V_DELIMITER)
        misc = _list_conllu_map(self.misc, Token.COMPONENT_DELIMITER)

        items = [id, form, lemma, upos, xpos, feats, head, deprel, deps, misc]
        return Token.FIELD_DELIMITER.join(items)
