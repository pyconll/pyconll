sentencetree
===================================

The ``sentencetree`` module is a light module which defines the ``create`` method for creating a ``Tree`` representation of a ``Sentence``. The ``sentencetree`` module replaces the previous ``SentenceTree`` class because of its unnecessary class structure, and confusing naming, since it was a simple combination of its two components rather than an actual ``Tree``. The data on the nodes in the ``Tree`` returned by ``create`` are ``Tokens`` which can be accessed through the node's ``data`` member.

This wrapper is very bare currently and only creates the tree based representation, without additional logic. Please create a github issue if you would like to see functionality added in this area!

API
----------------------------------
.. automodule:: pyconll.sentencetree
    :members:
    :special-members:
    :exclude-members: __dict__, __weakref__
