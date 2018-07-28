import requests

from pyconll._parser import iter_sentences
from pyconll.unit import Conll


def load_from_string(source):
    """
    Load CoNLL-U source in a string into a Conll object.

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


def load_from_file(filename):
    """
    Load a CoNLL-U file given the filename where it resides.

    Args:
        filename: The location of the file.

    Returns:
        A Conll object equivalent to the provided file.

    Raises:
        IOError: If there is an error opening the given filename.
        ParseError: If there is an error parsing the input into a Conll object.
    """
    with open(filename) as f:
        c = Conll(f)

    return c


def load_from_url(url):
    """
    Load a CoNLL-U file that is pointed to by a given URL.

    Args:
        url: The URL that points to the CoNLL-U file.

    Returns:
        A Conll object equivalent to the provided file.

    Raises:
        requests.exceptions.RequestException: If the url was unable to be properly
            retrieved and status was 4xx or 5xx.
        ParseError: If there is an error parsing the input into a Conll object.
    """
    resp = requests.get(url)
    resp.raise_for_status()

    resp.encoding = 'utf-8'
    lines = resp.text.splitlines()
    c = Conll(lines)

    return c


def iter_from_string(source):
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


def iter_from_file(filename):
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
    with open(filename) as f:
        for sentence in iter_sentences(f):
            yield sentence


def iter_from_url(url):
    """
    Iterate over a CoNLL-U file that is pointed to by a given URL.

    Args:
        url: The URL that points to the CoNLL-U file.

    Yields:
        The sentences that make up the CoNLL-U file.

    Raises:
        requests.exceptions.RequestException: If the url was unable to be properly
            retrieved.
        ParseError: If there is an error parsing the input into a Conll object.
    """
    resp = requests.get(url)
    resp.raise_for_status()

    lines = resp.text.splitlines()
    for sentence in iter_sentences(lines):
        yield sentence
