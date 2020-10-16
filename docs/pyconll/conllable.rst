conllable
===================================

``Conllable`` marks a class that can be output as a CoNLL formatted string. ``Conllable`` classes implement a ``conll`` method.

This is an abstract base class, and so no pure ``Conllable`` instance can be created. Instead this serves as an interface, marking types which have an expectation of supporting serialization. This consists of classes such as ``Conll``, ``Sentence``, and ``Token``, which are unified by this interface.

API
----------------------------------
.. automodule:: pyconll.conllable
    :members:
