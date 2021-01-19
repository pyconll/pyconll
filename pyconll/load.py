"""
A wrapper around the Conll class to easily load treebanks from multiple formats.
This module can also load resources by iterating over treebank data without
storing Conll objects in memory. This module is the main entrance to pyconll's
functionalities.
"""

from typing import Iterator

from pyconll._parser import iter_sentences
from pyconll.unit.conll import Conll
from pyconll.unit.sentence import Sentence


def load_from_string(source: str) -> Conll:
    """
    Load the CoNLL-U source in a string into a Conll object.

    Args:
        source: The CoNLL-U formatted string.

    Returns:
        A Conll object equivalent to the provided source.

    Raises:
        ParseError: If there is an error parsing the input into a Conll object.
    """
    lines = source.splitlines()
    c = Conll(lines)

    return c


def load_from_file(filename: str) -> Conll:
    """
    Load a CoNLL-U file given its location.

    Args:
        filename: The location of the file.

    Returns:
        A Conll object equivalent to the provided file.

    Raises:
        IOError: If there is an error opening the given filename.
        ParseError: If there is an error parsing the input into a Conll object.
    """
    with open(filename, encoding='utf-8') as f:
        c = Conll(f)

    return c


def iter_from_string(source: str) -> Iterator[Sentence]:
    """
    Iterate over a CoNLL-U string's sentences.

    Use this method if you only need to iterate over the CoNLL-U file once and
    do not need to create or store the Conll object.

    Args:
        source: The CoNLL-U string.

    Yields:
        The sentences that make up the CoNLL-U file.

    Raises:
        ParseError: If there is an error parsing the input into a Conll object.
    """
    lines = source.splitlines()
    for sentence in iter_sentences(lines):
        yield sentence


def iter_from_file(filename: str) -> Iterator[Sentence]:
    """
    Iterate over a CoNLL-U file's sentences.

    Args:
        filename: The name of the file whose sentences should be iterated over.

    Yields:
        The sentences that make up the CoNLL-U file.

    Raises:
        IOError if there is an error opening the file.
        ParseError: If there is an error parsing the input into a Conll object.
    """
    with open(filename, encoding='utf-8') as f:
        for sentence in iter_sentences(f):
            yield sentence
