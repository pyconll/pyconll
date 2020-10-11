conllable
===================================

``Conllable`` marks a class that can be output as a CoNLL formatted string. ``Conllable`` classes implement a ``conll`` method.

This is an abstract base class, and so no pure ``Conllable`` instance can be created. Instead this serves as an interface, marking objects which have an expectation of serializing data. This consists of classes such as ``Conll``, ``Sentence``, and ``Token``, which are unified by this api.

API
----------------------------------
.. automodule:: pyconll.conllable
    :members:
