from pyconllu._parser import iter_sentences
from pyconllu.unit import Conllu


def load_from_string(source):
    """
    Load CoNLL-U source in a string into a Conllu object.

    Args:
    source: The CoNLL-U formatted string.

    Returns:
    A Conllu object equivalent to the provided source.
    """
    lines = source.splitlines()
    c = Conllu(lines)

    return c


def load_from_file(filename):
    """
    Load a CoNLL-U file given the filename where it resides.

    Args:
    filename: The location of the file.

    Returns:
    A Conllu object equivalent to the provided file.
    """
    with open(filename) as f:
        c = Conllu(f)

    return c


def iter_from_string(source):
    """
    Iterate over a CoNLL-U string's sentences.

    Use this method if you only need to iterate over the CoNLL-U file once and
    do not need to create or store the Conllu object.

    Args:
    source: The CoNLL-U string.

    Returns:
    An iterator that yields consecutive sentences.
    """
    lines = source.splitlines()
    for sentence in iter_sentences(lines):
        yield sentence


def iter_from_file(filename):
    """
    Iterate over a CoNLL-U file's sentences.

    Args:
    fiilename: The name of the file whose sentences should be iterated over.

    Returns:
    An iterator that yields consecutive sentences.
    """
    with open(filename) as f:
        for sentence in iter_sentences(f):
            yield sentence
