conll
===================================

.. note::
    For loading new ``Conll`` objects from a file or string, prefer the load_ module which provides the main entry points for parsing CoNLL.

This module represents a CoNLL file, i.e. a collection of CoNLL annotated sentences. Like other collections in python, ``Conll`` objects can be indexed, sliced, iterated, etc (specifically it implements the MutableSequence_ contract). ``Conll`` objects are Conllable, so then can be converted into a CoNLL string or they can be written to file directly with the ``write`` method.

.. _load: ../load.html
.. _Conllable: ../conllable.html
.. _MutableSequence: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSequence


API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: pyconll.unit.conll
    :members:
    :exclude-members: __dict__, __weakref__
