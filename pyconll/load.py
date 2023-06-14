"""
A wrapper around the Conll class to easily load treebanks from multiple formats.
This module can also load resources by iterating over treebank data without
storing Conll objects in memory. This module is the main entrance to pyconll's
functionalities.
"""

import os
from typing import Iterable, Iterator, Union

from pyconll._parser import iter_sentences
from pyconll.unit.conll import Conll
from pyconll.unit.sentence import Sentence

PathLike = Union[str, bytes, os.PathLike]


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


def load_from_file(file_descriptor: PathLike) -> Conll:
    """
    Load a CoNLL-U file given its location.

    Args:
        file_descriptor: The file to load the CoNLL-U data from. This can be a
            filepath as a Path object, or string, or a file descriptor.

    Returns:
        A Conll object equivalent to the provided file.

    Raises:
        IOError: If there is an error opening the given filename.
        ParseError: If there is an error parsing the input into a Conll object.
    """
    with open(file_descriptor, encoding='utf-8') as f:
        c = Conll(f)

    return c


def load_from_resource(resource: Iterable[str]) -> Conll:
    """
    Load a CoNLL-U file from a generic string resource.

    Args:
        resource: The generic string resource. Each string from the resource is
            assumed to be a line in a CoNLL-U formatted resource.

    Returns:
        A Conll object equivalent to the string resource provided.

    Raises:
        ParseError: If there is an error parsing the input into a Conll object.
    """
    return Conll(resource)


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


def iter_from_file(file_descriptor: PathLike) -> Iterator[Sentence]:
    """
    Iterate over a CoNLL-U file's sentences.

    Args:
        file_descriptor: The file to iterate the CoNLL-U data from. This can be a
            filepath as a Path object, or string, or a file descriptor.

    Yields:
        The sentences that make up the CoNLL-U file.

    Raises:
        IOError: If there is an error opening the file.
        ParseError: If there is an error parsing the input into a Conll object.
    """
    with open(file_descriptor, encoding='utf-8') as f:
        for sentence in iter_sentences(f):
            yield sentence


def iter_from_resource(resource: Iterable[str]) -> Iterator[Sentence]:
    """
    Iterate over the sentences from an iterable string resource.

    This is a generic method that allows for any general resource that can
    provide data (like a streaming network request or memory mapped data) to be
    parsed as a CoNLL-U data source.

    Args:
        resource: The line source. Each iterated string should be a line in a
            CoNLL-U formatted file.

    Yields:
        The sentences that make up the CoNLL-U file.

    Raises:
        ParseError: If there is an error parsing the input into a Conll object.
    """
    for sentence in iter_sentences(resource):
        yield sentence
