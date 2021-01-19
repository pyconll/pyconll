"""
A library whose purpose is to provide a low level layer between the CoNLL format
and python code.
"""

__all__ = ['conllable', 'exception', 'load', 'tree', 'unit', 'util']

from .load import load_from_string, load_from_file, iter_from_string, \
       iter_from_file
from ._version import __version__
