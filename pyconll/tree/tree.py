"""
A general immutable tree module. This module is used when parsing a serial
sentence into a Tree structure.
"""

from typing import Generic, Iterator, List, Optional, TypeVar, overload

T = TypeVar('T')


class Tree(Generic[T]):
    """
    A tree node. This is the base representation for a tree, which can have many
    children which are accessible via child index. The tree's structure is
    immutable, so the data, parent, children cannot be changed once created.

    As is this class is useless, and must be created with the TreeBuilder
    module which is a sort of friend class of Tree to maintain its immutable
    public contract.
    """
    def __init__(self, data: T) -> None:
        """
        Create a tree holding the value. Create a larger Tree, with TreeBuilder.

        Args:
            data: The data to put with the Tree node.
        """
        self._data: T = data
        self._parent: Optional['Tree[T]'] = None
        self._children: List['Tree[T]'] = []

    @property
    def data(self) -> T:
        """
        The data on the tree node. The property ensures it is readonly.

        Returns:
            The data stored on the Tree.
        """
        return self._data

    @property
    def parent(self) -> Optional['Tree[T]']:
        """
        Provides the parent of the Tree. The property ensures it is readonly.

        Returns:
            A pointer to the parent Tree reference. None if there is no parent.
        """
        return self._parent

    @overload
    def __getitem__(self, key: int) -> 'Tree[T]':
        pass

    @overload
    def __getitem__(self, key: slice) -> List['Tree[T]']:
        pass

    def __getitem__(self, key):
        """
        Get specific children from the Tree. This can be an integer or slice.

        Args:
            key: The indexer for the item.
        """
        return self._children[key]

    def __iter__(self) -> Iterator['Tree[T]']:
        """
        Provides an iterator over the children.
        """
        for child in self._children:
            yield child

    def __len__(self) -> int:
        """
        Provides the number of direct children on the tree.

        Returns:
            The number of direct children on the tree.
        """
        return len(self._children)
