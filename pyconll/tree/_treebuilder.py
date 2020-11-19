"""
Defines a TreeBuilder module that will actually create a Tree. This class is
essentially a friend class of the Tree, so that the API of Tree can remain
immutable while allowing efficient creation of a new Tree in an easy fluent way.
"""

from typing import Any, Generic, TypeVar

from pyconll.tree.tree import Tree

T = TypeVar('T')


class TreeBuilder(Generic[T]):
    """
    A TreeBuilder is a utility to create arbitrary, immutable Trees. TreeBuilder
    works by traversing and creating a tree structure, and then providing an
    immutable view of the Tree on build. A TreeBuilder has an internal cursor
    on a Tree's node.

    A TreeBuilder can be reused to create many trees. This is useful if many
    similar Trees must be created. Note however, that if multiple Trees are
    created from the same TreeBuilder, Tree nodes will be unique, but data on
    the nodes will be shallow copies.
    """
    def __init__(self) -> None:
        """
        Creates a new empty TreeBuilder, with no internal data.
        """
        # Unfortunately, these must remain at Any since mypy cannot infer the
        # None check properly in _assert_initialization_status.
        self.root: Any = None
        self.current: Any = None
        self.constructed: bool = False

    def create_root(self, data: T) -> None:
        """
        Creates the root of the tree. This is the first step in Tree building.

        This should be called when a TreeBuilder is first created.

        Args:
            data: The optional data to put on the root node.
        """
        self.root = Tree(data)
        self.current = self.root

    def move_to_parent(self) -> None:
        """
        Move the internal cursor of the TreeBuilder to cursor location's parent.

        Raises:
            ValueError: If the TreeBuilder's root has not been initialized, or
                if the builder is already at the root.
        """
        self._assert_initialization_status()
        if self.current is self.root:
            raise ValueError('Currently at root. Cannot move to parent')

        self.current = self.current.parent

    def move_to_child(self, i: int) -> None:
        """
        Move the internal cursor to the cursor location's i-th child.

        Args:
            i: The index of the child to move to.

        Raises:
            IndexError: If the child index is out of range.
            ValueError: If the TreeBuilder's root has not been initialized.
        """
        self._assert_initialization_status()

        try:
            self.current = self.current[i]
        except IndexError as e:
            raise IndexError(
                '{}-th child is out of range. There are {} children on this node'
                .format(i, len(self.current))) from e

    def move_to_root(self) -> None:
        """
        Move the internal cursor to the root of the entire tree.

        Raises:
            ValueError: If the TreeBuilder's root has not been initialized.
        """
        self._assert_initialization_status()
        self.current = self.root

    def set_data(self, data: T) -> None:
        """
        Sets the data for the cursor location's node.

        Args:
            data: The data to place on the current cursor location's node.

        Raises:
            ValueError: If the TreeBuilder's root has not been initialized.
        """
        self._assert_initialization_status()
        self._copy_if_necessary()
        self.current._data = data

    def remove_child(self, i: int) -> None:
        """
        Remove the i-th child from the cursor location.

        Args:
            i: The index of the child to remove.

        Raises:
            IndexError: If the child is out of range.
            ValueError: If the TreeBuilder's root has not been initialized.
        """
        self._assert_initialization_status()
        self._copy_if_necessary()

        try:
            del self.current._children[i]
        except IndexError as e:
            raise IndexError(
                '{}-th child is out of range. There are {} children on this node'
                .format(i, len(self.current))) from e

    def add_child(self, data: T, move: bool = False) -> None:
        """
        Adds a child to the current cursor location's node.

        Children indices are directly related to the order of their creation.

        Args:
            data: The data to put on the created child.
            move: Flag to indicate if the cursor should move to this child.

        Raises:
            ValueError: If the TreeBuilder's root has not been initialized.
        """
        self._assert_initialization_status()
        self._copy_if_necessary()

        child: Tree[T] = Tree(data)
        child._parent = self.current
        self.current._children.append(child)

        if move:
            l = len(self.current)
            self.move_to_child(l - 1)

    def build(self) -> Tree[T]:
        """
        Provides an immutable reference to the constructed tree.

        Returns:
            The constructed Tree reference.

        Raises:
            ValueError: If the TreeBuilder's root has not been initialized.
        """
        self._assert_initialization_status()
        self.constructed = True
        return self.root

    def _copy_if_necessary(self) -> None:
        """
        Checks if a copy is necessary because the Tree has been built.
        """
        if self.constructed:
            self._copy()
            self.constructed = False

    def _copy(self) -> None:
        """
        Internal method to copy the constructed Tree in memory.
        """
        new_root: Tree[T] = Tree(self.root.data)

        new_current = None
        if self.current is self.root:
            new_current = new_root

        queue = [(new_root, self.root._children)]
        while queue:
            new_parent, children = queue.pop()

            new_children = []
            for child in children:
                new_child: Tree[T] = Tree(child.data)
                new_child._parent = new_parent
                new_children.append(new_child)

                queue.append((new_child, child._children))

                if self.current is child:
                    new_current = new_child

            new_parent._children = new_children

        self.root = new_root
        self.current = new_current

    def _assert_initialization_status(self) -> None:
        """
        Asserts the initialization invariant on the root of this builder.

        Raises:
            ValueError: If the TreeBuilder's root has not been initialized.
        """
        if self.root is None:
            raise ValueError(
                'The TreeBuilder has not created a root for the Tree yet')
