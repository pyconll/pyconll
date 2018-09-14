class ParseError(ValueError):
    """
    Error that results from an improper value into a parsing routine.
    """
    pass


class FormatError(ValueError):
    """
    Error that results from trying to format a CoNLL object to a string.
    """
    pass
