"""
Defines a base immutable tree type. This type can then be used to create a
TokenTree which maps a sentence. This type is meant to be limited in scope and
use and not as a general tree builder module.
"""


class Tree:
    """
    A tree node. This is the base representation for a tree, which can have many
    children which are accessible via child index. The tree's structure is
    immutable, so the parent and children cannot be changed once created.
    """

    def __init__(self, data, children):
        """
        Create a new tree with the desired properties.

        Args:
            data: The data to store on the tree.
            children: The children of this node. None if there are no children.
        """
        self.data = data
        self._parent = None

        if not children:
            self._children = []
        else:
            for child in children:
                child._parent = self

            self._children = children

    @property
    def children(self):
        """
        Provides the children of the Tree. The property ensures it is readonly.

        Returns:
            The list of children nodes.
        """
        return self._children

    @property
    def parent(self):
        """
        Provides the parent of the Tree. The property ensures it is readonly.

        Returns:
            A pointer to the parent Tree reference.
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
