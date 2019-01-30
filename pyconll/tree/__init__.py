"""
Defines the utilties for interfacing with CoNLL sentences as trees. These
include a base Tree class, and a SentenceTree class which when provided a Sentence
constructs the appropriate / corresponding tree structure.
"""

__all__ = ['tree', 'sentencetree']

from .tree import Tree, TreeBuilder
from .sentencetree import SentenceTree
