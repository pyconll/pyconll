tree
===================================

``Tree`` is a very basic immutable tree class. A ``Tree`` can have multiple children and has one parent. The parent and child of a tree are established when a ``Tree`` is created. Accessing the data on a ``Tree`` can be done through the ``data`` member. A ``Tree`` is created through the ``TreeBuilder`` module which is an internal API in pyconll. A ``Tree``'s use in pyconll is when creating a Tree structure from a ``Sentence`` object in the ``sentencetree`` module.

API
----------------------------------
.. automodule:: pyconll.tree.tree
    :members:
    :special-members:
    :exclude-members: __dict__, __weakref__
