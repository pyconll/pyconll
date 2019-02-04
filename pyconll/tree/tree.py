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

    def create_root(self, data=None):
        """
        Creates the root of the tree. This is the first step in Tree building.

        This should be called when a TreeBuilder is first created.

        Args:
            data: The optional data to put on the root node.
        """
        self.root = Tree()
        if data is not None:
            self.root.data = data
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
        self.current = self.current.children[i]

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
        self.current.data = data

    def remove_child(self, i):
        """
        Remove the i-th child from the cursor location.

        Args:
            i: The index of the child to remove.
        """
        self._copy_if_necessary()
        self.current.children.remove(i)

    def add_child(self, data=None, move=False):
        # TODO: consider the data=None problem.
        """
        Adds a child to the current cursor location's node.

        Children indices are directly related to the order of their creation.

        Args:
            data: The optional data to put on the created child.
            move: Flag to indicate if the cursor should move to this child.
        """
        self._copy_if_necessary()

        child = Tree()
        if data is not None:
            child.data = data
        child._parent = self.current

        self.current.children.append(child)

        if move:
            l = len(self.current.children)
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
        new_root.data = self.root.data

        queue = [(new_root, self.root.children)]
        while len(queue) > 0:
            new_parent, children = queue.pop()

            new_children = []
            for child in children:
                new_child = Tree()
                new_child.data = child.data
                new_children.append(new_child)

                queue.append((new_child, child.children))

            new_parent.children = new_children

        self.root = new_root
        self.current = new_current


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
