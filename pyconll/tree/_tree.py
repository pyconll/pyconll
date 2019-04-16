"""
A general tree module. This module includes a Builder to create the actual Tree
and the immutable Tree definition.
"""


class TreeBuilder:
    """
    A TreeBuilder is a utility to create arbitary, immutable Trees. TreeBuilder
    works by traversing and creating a tree structure, and then providing an
    immutable view of the Tree on build. A TreeBuilder has an internal cursor
    on a Tree's node.

    A TreeBuilder can be reused to create many trees. This is useful if many
    similar Trees must be created. Note however, that if multiple Trees are
    created from the same TreeBuilder, Tree nodes will be unique, but data on
    the nodes will be shallow copies.
    """

    def __init__(self):
        """
        Creates a new empty TreeBuilder, with no internal data.
        """
        self.root = None
        self.current = None
        self.constructed = False

    def create_root(self, data):
        """
        Creates the root of the tree. This is the first step in Tree building.

        This should be called when a TreeBuilder is first created.

        Args:
            data: The optional data to put on the root node.
        """
        self.root = Tree()
        self.root._data = data
        self.current = self.root

    def move_to_parent(self):
        """
        Move the internal cursor of the TreeBuilder to cursor location's parent.
        """
        self.current = self.current.parent

    def move_to_child(self, i):
        """
        Move the internal cursor to the cursor location's i-th child.

        Args:
            i: The index of the child to move to.
        """
        self.current = self.current[i]

    def move_to_root(self):
        """
        Move the internal cursor to the root of the entire tree.
        """
        self.current = self.root

    def set_data(self, data):
        """
        Sets the data for the cursor location's node.

        Args:
            data: The data to place on the current cursor location's node.
        """
        self._copy_if_necessary()
        self.current._data = data

    def remove_child(self, i):
        """
        Remove the i-th child from the cursor location.

        Args:
            i: The index of the child to remove.
        """
        self._copy_if_necessary()
        self.current._children.remove(i)

    def add_child(self, data, move=False):
        """
        Adds a child to the current cursor location's node.

        Children indices are directly related to the order of their creation.

        Args:
            data: The data to put on the created child.
            move: Flag to indicate if the cursor should move to this child.
        """
        self._copy_if_necessary()

        child = Tree()
        child._data = data
        child._parent = self.current
        self.current._children.append(child)

        if move:
            l = len(self.current)
            self.move_to_child(l - 1)

    def build(self):
        """
        Provides an immutable reference to the constructed tree.

        Returns:
            The constructed Tree reference.
        """
        self.constructed = True
        return self.root

    def _copy_if_necessary(self):
        """
        Checks if a copy is necessary because the Tree has been built.
        """
        if self.constructed:
            self._copy()
            self.constructed = False

    def _copy(self):
        """
        Internal method to copy the constructed Tree in memory.
        """
        new_root = Tree()
        new_root._data = self.root.data

        new_current = None
        if self.current is self.root:
            new_current = new_root

        queue = [(new_root, self.root._children)]
        while queue:
            new_parent, children = queue.pop()

            new_children = []
            for child in children:
                new_child = Tree()
                new_child._data = child.data
                new_child._parent = new_parent
                new_children.append(new_child)

                queue.append((new_child, child._children))

                if self.current is child:
                    new_current = new_child

            new_parent._children = new_children

        self.root = new_root
        self.current = new_current


class Tree:
    """
    A tree node. This is the base representation for a tree, which can have many
    children which are accessible via child index. The tree's structure is
    immutable, so the data, parent, children cannot be changed once created.
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
