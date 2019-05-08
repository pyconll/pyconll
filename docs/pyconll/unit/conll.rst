conll
===================================

This module represents a CoNLL file: a collection of CoNLL annotated sentences. Users should use the load_ module to create CoNLL objects rather than directly using the class constructor. The ``Conll`` object is a wrapper around a list of sentences that can be serialized into a CoNLL format, i.e. it is Conllable_.

``Conll`` is a subclass of ``MutableSequence``, so ``append``, ``reverse``, ``extend``, ``pop``, ``remove``, and ``__iadd__`` are available free of charge, even though they are not defined below. This information can be found on the collections_ documentation.

.. _load: ../load.html
.. _Conllable: ../conllable.html
.. _collections: https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes


API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: pyconll.unit.conll
    :members:
    :exclude-members: __dict__, __weakref__
