token
===================================

The Token module represents a CoNLL token annotation. In a CoNLL file, this is a non-empty, non-comment line. ``Token`` members correspond directly with the Universal Dependencies CoNLL definition and all members are stored as strings. This means ids are strings as well. These fields are: ``id``, ``form``, ``lemma``, ``upos``, ``xpos``, ``feats``, ``head``, ``deprel``, ``deps``, ``misc``. More information on these is found below.

Fields
-----------------------------------
All fields are strings except for ``feats``, ``deps``, and ``misc``, which are ``dicts``. Each of these fields has specific semantics per the UDv2 guidelines. Since these fields are ``dicts`` these means modifying them uses python's natural syntax for dictionaries, and there is no wrapping API.

feats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``feats`` is a key value mapping from ``str`` to ``set``. An example entry would be ``Gender``, and ``set((Feminine,))``. More features could be added to an existing key by adding to its set, or a new feature could be added by adding to the dictionary. Note that any keys with empty ``sets`` will throw an error, as all features must have at least one value.

deps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``deps`` is a key value mapping from ``str`` to ``tuple`` of cardinality 4, which represents enhanced dependencies. The key is the index of the token head, and the tuple elements define the enhanced dependency. Most Universal Dependencies treebanks, only use 2 of these 4 dimensions: the token index and the relation. See the Universal Dependencies guideline for more information on these 4 components. When adding new ``deps``, the values must also be tuples of cardinality 4.

misc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Lastly, for ``misc``, the documentation only specifies that values be separated by a '|'. Not all keys have to have a value. So, values on ``misc`` are either ``None``, or a ``set`` of ``str``. A key with a value of ``None`` is output as a singleton, with no separating '='.


Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Below is an example of adding a new feature to a token, where the key must first be initialized:

.. code-block:: python

    token.feats['NewFeature'] = set(('No', ))

or alternatively as:

.. code-block:: python

    token.feats['NewFeature'] = set()
    token.feats['NewFeature'].add('No')

On the miscellaneous column, adding a singleton field is done with the following line:

.. code-block:: python

    token.misc['SingletonFeature'] = None


API
----------------------------------
.. automodule:: pyconll.unit.token
    :members:
    :special-members:
    :exclude-members: __dict__, __weakref__
