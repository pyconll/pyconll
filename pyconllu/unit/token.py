def _is_underscore(s):
    """
    Checks if the provided string is an underscore.

    Args:
    The string to check.

    Returns:
    True if the string is an underscore and False otherwise.
    """
    return s == '_'

def _unit_empty_map(value):
    """
    Map unit values for CoNLL-U columns that are empty to a value of None.

    Args:
    value: The value to check for existence. Should be a string.

    Returns:
    None if value is an underscore and value otherwise.
    """
    return None if _is_underscore(value) else value

def _dict_empty_map(values, delim, av_separator, v_delimiter):
    """
    Map dict based values for CoNLL-U columns that are empty to an empty dict.

    Args:
    values: The value to check for existence. Should be a string.
    delim: The delimiter between values in the provided string.
    av_separator: The attribute-value separator in the provided string.
    v_delimiter: The delimiter between values for the same attribute.

    Returns:
    An empty dict if value is an underscore. Otherwise, a dict of key-value
    pairs split on the Token feature delimiter.
    """
    if _is_underscore(values):
        return {}
    else:
        d = {}
        for el in values.split(value_delimiter):
            k, v = el.split(av_separator)
            v = set(v.split(v_delimiter))
            d[k] = v

        return d

def _list_empty_map(values, delim):
    """
    Map list based values for CoNLL-U columns that are empty to an empty list.

    Args:
    values: The value to check for existence. Should be a string.
    delim: The delimiter between values in the provided string.

    Returns:
    An empty list if the value is an underscore and a list of the values
    otherwise.
    """
    return [] if _is_underscore(values) else values.split(delim)

def _unit_conllu_map(value):
    """
    Map a unit value to its CoNLL-U format equivalent.

    Args:
    value: The value to convert to its CoNLL-U format. Should be a string.

    Returns:
    '_' if value is None and value otherwise.
    """
    return '_' if value is None else value

def _dict_conllu_map(values, delim, av_separator, v_delimiter):
    """
    Map a dict based value to its CoNLL-U format equivalent.

    This CoNLL-U format will be sorted alphabetically by attribute.

    Args:
    values: The dict to convert to its CoNLL-U format.
    delim: The delimiter between values in the output.
    av_separator: The attribute-value separator in the provided string.
    v_delimiter: The delimiter between values in attribute-value pairs.

    Returns:
    The CoNLL-U format as a string.
    """
    if values == {}:
        return '_'
    else:
        sorted_d = sorted(values.items(), key=lambda k, v: k)
        for pair in sorted_d:
            pair[1] = sorted(pair[1], key=str.lower).join(v_delimiter)

        return
            [pair.join(av_separator) for pair in sorted_d].join(delim)

def _list_conllu_map(values, delim):
    """
    Map a list to its CoNLL-U format equivalent.

    Args:
    values: The list to convert to its CoNLL-U format.
    delim: The delimiter between the values of the list.

    Returns:
    The CoNLL-U format as a string.
    """
    # TODO: Remove '_' and use empty marker.
    return '_' if values == [] else values.join(delim)


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

    def __init__(self, line):
        """
        Construct the token from the given line. A Token line must end in an an
        LF line break according to the specification. However, this method will
        accept a line with or without this ending line break.

        Args:
        line: The line that represents the Token in CoNLL-U format.
        """
        if line[-1] == '\n':
            line = line[:-1]

        fields = line.split(Token.FIELD_DELIMITER)

        # Assign all the field values from the line to internal equivalents.
        # TODO: How to properly handle underscores.
        # NOTE: Multiword tokens have '_' in all fields except 2
        self.id = fields[0]
        self.form = _unit_empty_map(fields[1])
        self.lemma = _unit_empty_map(fields[2])
        self.upos = _unit_empty_map(fields[3])
        self.xpos = _unit_empty_map(fields[4])
        self.feats = _dict_empty_map(fields[5], Token.COMPONENT_DELIMITER,
            Token.AV_SEPARATOR, Token.V_DELIMITER)
        self.head = _unit_empty_map(fields[6])
        self.deprel = _unit_empty_map(fields[7])
        self.deps = _dict_empty_map(fields[8], Token.COMPONENT_DELIMITER,
            Token.AV_SEPARATOR, Token.V_DELIMITER)
        self.misc = _list_empty_map(fields[9], Token.COMPONENT_DELIMITER)

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
