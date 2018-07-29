token
===================================

The Token module represents a single token (multiword or otherwise) in a CoNLL-U file. In text, this corresponds to one non-empty, non-comment line. Token has several members that correspond with the columns of the lines. All values are stored as strings. So ids are strings and not numeric. These fields are listed below and coresspond exactly with those found in the Universal Dependencenies project:

.. highlight

id
form
lemma
upos
xpos
feats
head
deprel
deps
misc

.. highlight:: none


Fields
-----------------------------------
Currently, all fields are strings except for ``feats``, ``deps``, and ``misc``, which are ``dicts``. There are specific semantics for each of these according to the UDv2 guidelines. Again, the current approach is for these fields to be ``dicts`` as described below rather than providing an extra interface for these fields.

Since all of these fields are ``dicts``, modifying non existent keys will result in a ``KeyError``. This means that new values must be added as in a normal ``dict``. For ``set`` based ``dicts``, ``feats`` and specific fields of ``misc``, the new key must be assigned to an empty ``set`` to start. More details on this below.

feats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``feats`` is a dictionary of attribute value pairs, where there can be multiple values. So the values for ``feats`` is a ``set`` when parsed. The keys are ``str`` and the values are ``set``. Do not assign a value to a ``str`` or any other type. Note that any keys with empty ``sets`` will not be output.

deps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``deps`` is also a dictionary of attribute value pairs, but there is only one value, so the values are ``strings``.

misc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Lastly, for ``misc``, the documentation only specifies that the values are separated by a '|'. So the values can either be an attribute values pair like ``feats`` or it can be a single value. So for this reason, the value for ``misc`` is either ``None`` for entries with no '=', and an attribute values pair, otherwise, with the value being a ``set`` of ``str``. A key with a value of ``None`` is output as a singleton, while a key with an empty ``set`` is not output like with ``feats``.

When adding a new key, the key must first be initialized manually as so:

.. highlight

token.misc['NewFeature'] = set(('No', ))

.. highlight:: python

or alternatively as:

.. highlight

token.misc['NewFeature'] = set()
token.misc['NewFeature'].add('No')

.. highlight:: python


API
----------------------------------
.. automodule:: pyconll.unit.token
    :members:
    :special-members:
    :exclude-members: __dict__, __weakref__
