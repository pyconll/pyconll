conll
===================================

A collection of CoNLL annotated sentences. This collection should rarely be created by API callers, that is what the ``pyconll.load`` module is for which allows for easy APIs to load CoNLL files from a string or file (no network yet). The Conll object can be thought of as a simple list of sentences. There is very little more of a wrapper around this.

``Conll`` is a subclass of ``MutableSequence`` this means that ``append``, ``reverse``, ``extend``, ``pop``, ``remove``, and ``__iadd__`` are available free of charge. There is no implementation of them, but they are provided by ``MutableSequence`` by implementing the base abstract methods. This means that ``Conll`` behaves almost exactly like a ``list`` with the same methods.


API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: pyconll.unit.conll
    :members:
    :exclude-members: __dict__, __weakref__
