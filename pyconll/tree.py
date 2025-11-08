"""
A general immutable tree module. This module is used when parsing a serial sentence into a Tree
structure.
"""

from typing import Any, Callable, Iterator, Optional, Sequence, overload


class _TreeBuilder[T]:
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
            raise ValueError("Currently at root. Cannot move to parent")

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
                f"{i}-th child is out of range. There are {len(self.current)} children on this node"
            ) from e

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
                f"{i}-th child is out of range. There are {len(self.current)} children on this node"
            ) from e

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
            raise ValueError("The TreeBuilder has not created a root for the Tree yet")


class Tree[T]:
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
        self._parent: Optional["Tree[T]"] = None
        self._children: list["Tree[T]"] = []

    @property
    def data(self) -> T:
        """
        The data on the tree node. The property ensures it is readonly.

        Returns:
            The data stored on the Tree.
        """
        return self._data

    @property
    def parent(self) -> Optional["Tree[T]"]:
        """
        Provides the parent of the Tree. The property ensures it is readonly.

        Returns:
            A pointer to the parent Tree reference. None if there is no parent.
        """
        return self._parent

    @overload
    def __getitem__(self, key: int) -> "Tree[T]": ...

    @overload
    def __getitem__(self, key: slice) -> list["Tree[T]"]: ...

    def __getitem__(self, key):
        """
        Get specific children from the Tree. This can be an integer or slice.

        Args:
            key: The indexer for the item.
        """
        return self._children[key]

    def __iter__(self) -> Iterator["Tree[T]"]:
        """
        Provides an iterator over the children.
        """
        yield from self._children

    def __len__(self) -> int:
        """
        Provides the number of direct children on the tree.

        Returns:
            The number of direct children on the tree.
        """
        return len(self._children)


def _create_tree_helper[K, I](
    builder: _TreeBuilder, node: K, to_id: Callable[[K], I], children_tokens: dict[I, list[K]]
) -> None:
    """
    Method to help create a tree from a sentence given the root token.

    Args:
        builder: The TreeBuilder currently being used to create the Tree.
        node: The current token we are constructing the tree at.
        to_id: Callable that transforms a token into its id.
        children_tokens: A dictionary from token id to children tokens.

    Returns:
        A Tree constructed given the sentence structure.
    """
    try:
        tokens = children_tokens[to_id(node)]
    except KeyError:
        tokens = []

    for token in tokens:
        builder.add_child(data=token, move=True)
        _create_tree_helper(builder, token, to_id, children_tokens)
        builder.move_to_parent()


def from_tokens[K, I](
    tokens: Sequence[K],
    starting_id: I,
    to_id: Callable[[K], I],
    to_head: Callable[[K], I],
    skip: Optional[Callable[[K], bool]] = None,
) -> Tree[K]:
    """
    The completely generic function to create a Tree structure for a sequence of Tokens.

    This can be used for tokens other than the pre-defined CoNLL-U schema.

    Args:
        tokens: The tokens to create the tree from.
        starting_id: The root token of the tree will be a child of this id.
        to_id: The mapper from the token to its id.
        to_head: The mapper from the token to the id of its parent.
        skip: The optional guard to skip certain tokens that may not participate in the Tree
            structure.
    """
    children_tokens: dict[I, list[K]] = {}

    for token in tokens:
        if skip is not None and skip(token):
            continue

        h = to_head(token)
        try:
            children_tokens[h].append(token)
        except KeyError:
            children_tokens[h] = [token]

    builder: _TreeBuilder[K] = _TreeBuilder()
    starters = children_tokens.get(starting_id)
    if starters is None:
        raise ValueError("The current sentence has no root token.")

    if len(starters) != 1:
        raise ValueError("There should be exactly one root token in a sentence.")

    root_token = starters[0]
    builder.create_root(root_token)
    _create_tree_helper(builder, root_token, to_id, children_tokens)
    root = builder.build()
    return root
