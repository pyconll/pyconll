import pytest

from pyconll.tree import Tree


def test_empty_tree_creation():
    """
    Test that an empty tree with no data and no children.
    """
    t = Tree(None, None)

    assert len(t) == 0
    assert t.children == []
    assert t.data is None


def test_children_read_only():
    """
    Test that children on a Tree cannot be assigned after construction.
    """
    child1 = Tree(2, None)
    child2 = Tree(7, None)
    t = Tree(1, [child1])

    with pytest.raises(AttributeError):
        t.children = []


def test_parent_read_only():
    """
    Test that the parent field cannot be assigned after construction.
    """
    child1 = Tree(2, None)
    child2 = Tree(7, None)
    t = Tree(1, [child1, child2])

    with pytest.raises(AttributeError):
        t[0].parent = None


def test_get_children():
    """
    Test that we can properly retreive children from a tree by index.
    """
    child11 = Tree(13, None)
    child1 = Tree(2, [child11])
    child2 = Tree(7, None)

    t = Tree(1, [child1, child2])

    assert t[0] == child1
    assert t[1] == child2
    assert t[0][0] == child11


def test_iter_children():
    """
    Test that we can properly iterate over the children of a tree.
    """
    data = list(range(2, 15, 3))
    children = list(map(lambda el: Tree(el, None), data))

    t = Tree(0, children)

    for i, child in enumerate(t):
        assert child.data == data[i]


def test_len_children():
    """
    Test that we can properly get the number of children.
    """
    data = list(range(2, 15, 3))
    subdata = list(map(lambda el: Tree(el, None), [0, 1, 2]))
    children = list(map(lambda el: Tree(el, subdata), data))

    t = Tree(0, children)

    assert len(t) == len(data)
    for child in t:
        assert len(child) == len(subdata)


def test_parent_assigment():
    """
    Test that children tree's parents are properly assigned.
    """
    child11 = Tree(13, None)
    child1 = Tree(2, [child11])
    child2 = Tree(7, None)

    t = Tree(1, [child1, child2])

    assert t.parent is None
    assert child1.parent == t
    assert child2.parent == t
    assert child11.parent == child1
