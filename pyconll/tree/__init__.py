"""
Defines the utilties for interfacing with CoNLL sentences as trees. These
include a base Tree class, and a TokenTree class which when provided a Sentence
constructs the appropriate / corresponding tree structure.
"""

__all__ = ['tree', 'tokentree']

from .tree import Tree
from .tokentree import TokenTree
