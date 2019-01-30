"""
"""

class TreeBuilder:
    def __init__(self):
        """
        """
        self.root = Tree()
        self.current = self.root

    def move_to_parent(self):
        """
        """
        self.current = self.current.parent

    def move_to_child(self, i):
        """
        """
        self.current = self.current.children[i]

    def move_to_root(self):
        """
        """
        self.current = self.root

    def add_child(self, data=None, move=False):
        """
        """
        child = Tree()
        if data is not None:
            child.data = data
        child._parent = self.current

        self.current._children.append(child)

        if move:
            l = len(self.current._children)
            self.move_to_child(l - 1)

    def remove_child(self, i):
        """
        """
        self.current._children.remove(i)

    def set_data(self, data):
        """
        """
        self.current.data = data

    def build(self):
        """
        """
        return self.root


class Tree:
    """
    A tree node. This is the base representation for a tree, which can have many
    children which are accessible via child index. The tree's structure is
    immutable, so the parent and children cannot be changed once created.
    """

    def __init__(self):
        """
        Create a new tree with the desired properties.

        Args:
            data: The data to store on the tree.
            children: The children of this node. None if there are no children.
        """
        self.data = None
        self._parent = None
        self._children = []

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
