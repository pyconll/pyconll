import pytest

from pyconll.tree.tree import Tree
from pyconll.tree._treebuilder import TreeBuilder

from tests.tree.util import assert_tree_structure


def test_minimal_tree_creation():
    """
    Test creating the minimal tree using the constructor.
    """
    t = Tree(None)

    assert t.data is None
    assert t.parent is None
    assert len(t) == 0


def test_data_read_only():
    """
    Test that the data on a Tree cannot be assigned after construction.
    """
    t = Tree(None)
    with pytest.raises(AttributeError):
        t.data = 0


def test_parent_read_only():
    """
    Test that the parent field cannot be assigned after construction.
    """
    t = Tree(None)
    with pytest.raises(AttributeError):
        t.parent = None


def test_get_children():
    """
    Test that we can properly retreive children from a tree by index.
    """
    builder = TreeBuilder()
    builder.create_root(1)
    builder.add_child(7)
    builder.add_child(2, move=True)
    builder.add_child(13)
    t = builder.build()

    assert t[0].data == 7
    assert t[1].data == 2
    assert t[1][0].data == 13


def test_iter_children():
    """
    Test that we can properly iterate over the children of a tree.
    """
    builder = TreeBuilder()
    builder.create_root(0)

    data = list(range(2, 15, 3))
    for datum in data:
        builder.add_child(datum)
    t = builder.build()

    for i, child in enumerate(t):
        assert child.data == data[i]


def test_len_children():
    """
    Test that we can properly get the number of children.
    """
    builder = TreeBuilder()
    builder.create_root(0)

    data = list(range(2, 15, 3))
    subdata = [0, 1, 2, 3, 4]
    for datum in data:
        builder.add_child(datum, move=True)

        for subdatum in subdata:
            builder.add_child(subdatum)

        builder.move_to_parent()
    t = builder.build()

    assert len(t) == len(data)
    for child in t:
        assert len(child) == len(subdata)


def test_parent_assigment():
    """
    Test that children tree's parents are properly assigned.
    """
    builder = TreeBuilder()
    builder.create_root(0)
    builder.add_child(2, move=True)
    builder.add_child(13)
    builder.move_to_parent()
    builder.add_child(7)

    t = builder.build()

    assert t.parent is None
    assert t[0].parent == t
    assert t[1].parent == t
    assert t[0][0].parent == t[0]


def test_after_creation_copy():
    """
    Test that a single TreeBuilder can be used multiple times properly.
    """
    builder = TreeBuilder()
    builder.create_root(0)
    builder.add_child(2, move=True)
    builder.add_child(13)
    builder.move_to_parent()
    builder.add_child(7)

    t1 = builder.build()

    builder.move_to_root()
    builder.set_data(4)
    builder.add_child(3, move=True)
    builder.add_child(15)

    t2 = builder.build()

    assert t2 is not t1
    assert t2[0] is not t1[0]
    assert t2[0][0] is not t1[0][0]
    assert t2[1] is not t1[1]

    assert t2.data == 4
    assert t2[0].data == 2
    assert t2[0][0].data == 13
    assert t2[1].data == 7
    assert t2[2].data == 3
    assert t2[2][0].data == 15

    assert len(t2) == 3
    assert len(t2[0]) == 1
    assert len(t2[1]) == 0
    assert len(t2[2]) == 1


def test_cannot_operate_on_rootless():
    """
    Verify that operations do not work on a TreeBuilder when no root is created.
    """
    builder = TreeBuilder()

    with pytest.raises(ValueError):
        builder.move_to_root()

    with pytest.raises(ValueError):
        builder.move_to_parent()

    with pytest.raises(ValueError):
        builder.build()


def test_cannot_move_up_on_root():
    """
    Test that when at the root node, the builder cannot move up to a parent.
    """
    builder = TreeBuilder()

    builder.create_root(0)

    with pytest.raises(ValueError):
        builder.move_to_parent()


def test_cannot_move_out_of_range():
    """
    Test that the builder cannot move to a child that is out of index.
    """
    builder = TreeBuilder()

    builder.create_root(0)
    builder.add_child(5)

    with pytest.raises(IndexError):
        builder.move_to_child(3)


def test_cannot_remove_out_of_range():
    """
    Test that the builder cannot remove a child it does not have.
    """
    builder = TreeBuilder()

    builder.create_root(0)
    builder.add_child(5)

    with pytest.raises(IndexError):
        builder.remove_child(5)


def test_on_copy_not_on_root():
    """
    Test that the current pointer is relatively correct after a copy operation.
    """
    builder = TreeBuilder()
    builder.create_root(0)
    builder.add_child(5)
    builder.add_child(6, move=True)

    _ = builder.build()
    builder.add_child(7)

    t = builder.build()
    assert_tree_structure(t, {(): 0, (0, ): 5, (1, ): 6, (1, 0): 7})
