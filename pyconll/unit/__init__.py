"""
A collection of the pyconll types for interfacing with the CoNLL format. These
types are inter dependent in that Tokens make up Sentences which make up
a Conll treebank.
"""

__all__ = ['conll', 'sentence', 'token']

from .token import Token
from .sentence import Sentence
from .conll import Conll
