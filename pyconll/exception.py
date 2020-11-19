"""
Holds custom pyconll errors. These errors include parsing errors when reading
treebanks, and errors when outputting CoNLL objects.
"""


class ParseError(ValueError):
    """
    Error that results from an improper value into a parsing routine.
    """


class FormatError(ValueError):
    """
    Error that results from trying to format a CoNLL object to a string.
    """
