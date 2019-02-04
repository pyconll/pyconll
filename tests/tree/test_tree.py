import pytest

from pyconll.tree import Tree, TreeBuilder


def test_empty_tree_creation():
    """
    Test that an empty tree with no data and no children.
    """
    t = Tree()

    assert len(t) == 0
    assert t.data is None


def test_children_read_only():
    """
    Test that children on a Tree cannot be assigned after construction.
    """
    t = Tree()
    with pytest.raises(AttributeError):
        t.children = []


def test_parent_read_only():
    """
    Test that the parent field cannot be assigned after construction.
    """
    t = Tree()
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
    builder.create_root()

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
    builder.create_root()

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
    builder.create_root()
    builder.add_child(2, move=True)
    builder.add_child(13)
    builder.move_to_parent()
    builder.add_child(7)

    t = builder.build()

    assert t.parent is None
    assert t[0].parent == t
    assert t[1].parent == t
    assert t[0][0].parent == t[0]
