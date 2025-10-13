"""
A library whose purpose is to provide a low level layer between the CoNLL format
and python code.
"""

__all__ = ["conllable", "exception", "load", "tree", "unit", "util"]

from .load import Parser, get_default_parser
from ._version import __version__
