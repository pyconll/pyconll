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
Currently, all fields are strings except for ``feats``, ``deps``, and ``misc``, which are ``dicts``. There are specific semantics for each of these according to the UDv2 guidelines. The current approach is for these fields to be ``dicts`` as described below rather than providing an extra interface for these fields.

feats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``feats`` is a dictionary of attribute value pairs, where there can be multiple values. So the values for ``feats`` is a ``set`` when parsed. When assigning and changing the values in ``feats`` ensure that the values are ``sets``. Note that any keys with empty ``sets`` will not be output.

deps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``deps`` is also a dictionary of attribute value pairs, but there is only one value, so the values are strings.

misc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Lastly, for ``misc``, the documentation only specifies that the values are separated by a '|'. So for this reason, the value for ``misc`` is either ``None`` for entries with no '=', and an attribute value pair otherwise with the value being a ``string`` or a ``set``.


API
----------------------------------
.. automodule:: pyconll.unit.token
    :members:
    :special-members:
