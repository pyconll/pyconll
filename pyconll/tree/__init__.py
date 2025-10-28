"""
Defines a tree data structure for internal use within pyconll. This module's
logic is not intended to be used outside of pyconll, and is exposed here only
so that pyconll methods that expose the Tree data structure will have
appropriate documentation.
"""

__all__ = ['tree']

from .tree import Tree
