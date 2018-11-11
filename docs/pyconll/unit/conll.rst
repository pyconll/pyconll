conll
===================================

A collection of CoNLL annotated sentences. For creating new instances of this object, API callers should use the ``pyconll.load`` module to abstract over the resource type. The ``Conll`` object can be thought of as a simple wrapper around a list of sentences that can be serialized into a CoNLL format.

``Conll`` is a subclass of ``MutableSequence``, so ``append``, ``reverse``, ``extend``, ``pop``, ``remove``, and ``__iadd__`` are available free of charge, even though they are not defined below.


API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: pyconll.unit.conll
    :members:
    :exclude-members: __dict__, __weakref__
