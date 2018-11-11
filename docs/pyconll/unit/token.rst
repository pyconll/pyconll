token
===================================

The Token module represents a CoNLL token annotation. In a CoNLL file, this corresponds to a non-empty, non-comment line. ``Token`` members correspond directly with the Universal Dependencies CoNLL definition and all values are stored as strings. This means ids are strings as well. These fields are: ``id``, ``form``, ``lemma``, ``upos``, ``xpos``, ``feats``, ``head``, ``deprel``, ``deps``, ``misc``

Fields
-----------------------------------
All fields are strings except for ``feats``, ``deps``, and ``misc``, which are ``dicts``. Each of these fields has specific semantics per the UDv2 guidelines.

Since all of these fields are ``dicts``, modifying non existent keys will result in a ``KeyError``. This means that new values must be added as in a normal ``dict``. For ``set`` based ``dicts``, ``feats`` and specific fields of ``misc``, the new key must be assigned to an empty ``set`` to start. More details on this below.

feats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``feats`` is a key value mapping from ``str`` to ``set``. Note that any keys with empty ``sets`` will throw an error, as all keys must have at least one feature.

deps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``deps`` is a key value mapping from ``str`` to ``tuple`` of cardinality 4. Most Universal Dependencies treebanks, only use 2 of these 4 dimensions: the token index and the relation. See the Universal Dependencies guideline for more information on these 4 components.When adding new ``deps``, the values must also be tuples of cardinality 4. Note that ``deps`` parsing is broken before version 1.0.

misc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Lastly, for ``misc``, the documentation only specifies that the values are separated by a '|'. So not all components have to have a value. So, the values on ``misc`` are either ``None`` for entries with no '=', or ``set`` of ``str``. A key with a value of ``None`` is output as a singleton.


Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Below is an example of adding a new feature to a token, where the key must first be initialized:

.. code-block:: python

    token.feats['NewFeature'] = set(('No', ))

or alternatively as:

.. code-block:: python

    token.feats['NewFeature'] = set()
    token.feats['NewFeature'].add('No')


API
----------------------------------
.. automodule:: pyconll.unit.token
    :members:
    :special-members:
    :exclude-members: __dict__, __weakref__
