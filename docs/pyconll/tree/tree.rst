tree
===================================

``Tree`` is a very basic immutable tree class. A ``Tree`` can have multiple children and has one parent. The parent and child of a tree are established when a ``Tree`` is created. Accessing the data on a ``Tree`` can be done through the ``data`` member. A ``Tree``'s direct children can be iterated with a for loop. A ``Tree`` is created through the ``TreeBuilder`` module which is an internal module in pyconll and keeps the public interface immutable. A ``Tree`` is provided as the result of ``to_tree`` on a ``Sentence`` object.

API
----------------------------------
.. automodule:: pyconll.tree.tree
    :members:
    :special-members:
    :exclude-members: __dict__, __weakref__
