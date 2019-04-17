"""
A general immutable tree module. This module is used when parsing a serial
sentence into a Tree structure.
"""


class Tree:
    """
    A tree node. This is the base representation for a tree, which can have many
    children which are accessible via child index. The tree's structure is
    immutable, so the data, parent, children cannot be changed once created.

    As is this class is useless, and must be created with the TreeBuilder
    module which is a sort of friend class of Tree to maintain its immutable
    public contract.
    """

    def __init__(self):
        """
        Create a new empty tree. To create a useful Tree, use TreeBuilder.
        """
        self._data = None
        self._parent = None
        self._children = []

    @property
    def data(self):
        """
        The data on the tree node. The property ensures it is readonly.

        Returns:
            The data stored on the Tree. No data is represented as None.
        """
        return self._data

    @property
    def parent(self):
        """
        Provides the parent of the Tree. The property ensures it is readonly.

        Returns:
            A pointer to the parent Tree reference. None if there is no parent.
        """
        return self._parent

    def __getitem__(self, key):
        """
        Get specific children from the Tree. This can be an integer or slice.

        Args:
            key: The indexer for the item.
        """
        return self._children[key]

    def __iter__(self):
        """
        Provides an iterator over the children.
        """
        for child in self._children:
            yield child

    def __len__(self):
        """
        Provides the number of direct children on the tree.

        Returns:
            The number of direct children on the tree.
        """
        return len(self._children)
