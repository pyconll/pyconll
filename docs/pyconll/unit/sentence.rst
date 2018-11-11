sentence
===================================

The ``Sentence`` module represents an entire CoNLL sentence, which is composed of two main parts: the comments and the tokens.

Comments
----------------------------------
Comments are treated as key-value pairs, where the separating character between key and value is ``=``. If there is no ``=`` present then then the comment is treated as a singleton, where the key is the comment string and the corresponding value is ``None``. Read and write methods on this data can be found on methods prefixed with ``meta_``.

For convenience, the id and text of a sentence can be accessed through member properties directly rather than through metadata methods. So ``sentence.id``, rather than ``sentence.meta_value('id')``. Since this API does not support changing a token's form, the ``text`` comment cannot be changed.

Document and Paragraph ID
----------------------------------
The document and paragraph id of a sentence are automatically inferred from a CoNLL treebank given sentence comments. Reassigning ids must be done through comments on the sentence level, and there is no API for simplifying this reassignment.

Tokens
----------------------------------
These are the meat of the sentence. Tokens can be accessed through their id defined in the CoNLL annotation as a string or as a numeric index. So the same indexing syntax understands, ``sentence['5']``, ``sentence['2-3']`` and ``sentence[2]``.


API
----------------------------------
.. automodule:: pyconll.unit.sentence
    :members:
    :exclude-members: __dict__, __weakref__
