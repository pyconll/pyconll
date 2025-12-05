token
===================================

.. note::
    For working with CoNLL-U tokens, see the conllu_ module which provides the standard ``Token`` class. This page describes the general concept of tokens in pyconll.

In pyconll, tokens are defined using the ``TokenSchema`` protocol. The most common token type is the CoNLL-U ``Token`` from the ``pyconll.conllu`` module, which represents a CoNLL-U token annotation with 10 standard columns.

For CoNLL-U specifically, token fields correspond directly with the `Universal Dependencies CoNLL-U format`__: ``id``, ``form``, ``lemma``, ``upos``, ``xpos``, ``feats``, ``head``, ``deprel``, ``deps``, ``misc``.

.. _conllu: ../conllu.html
__ https://universaldependencies.org/format#conll-u-format

Fields
-----------------------------------
All fields are optional strings except for ``feats``, ``deps``, and ``misc``, which are ``dicts``. As optional strings, they can either be None, or a string value. Fields which are dictionaries have specific semantics per the UDv2 guidelines. Since these fields are ``dicts`` this means modifying them uses python's natural syntax for dictionaries.

feats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``feats`` is a key-value mapping from ``str`` to ``set``. An example entry would be key ``Gender`` with value ``set((Feminine,))``. More features could be added to an existing key by adding to its set, or a new feature could be added by adding to the dictionary. All features must have at least one value, so any keys with empty sets will throw an error on serialization back to text.

deps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``deps`` is a key-value mapping from ``str`` to ``tuple`` of cardinality 4. This field represents enhanced dependencies. The key is the index of the token head, and the tuple elements define the enhanced dependency. Most Universal Dependencies treebanks, only use 2 of these 4 dimensions: the token index and the relation. See the `Universal Dependencies guideline`__ for more information on these 4 components. When adding new ``deps``, the values must also be tuples of cardinality 4.

misc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For ``misc``, the documentation only specifies that values be separated by a '|', so not all keys have to have a value. So, values on ``misc`` are either ``None``, or a ``set`` of ``str``. A key with a value of ``None`` is output as a singleton, with no separating '='. A key with a corresponding ``set`` value will be handled like ``feats``.


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


CoNLL-U Token API
----------------------------------

For the complete CoNLL-U Token implementation, see the conllu_ module documentation.

You can also define custom token schemas - see the schema_ module for details on creating your own token types for different formats.

.. _schema: ../schema.html

__ https://universaldependencies.org/u/overview/enhanced-syntax.html