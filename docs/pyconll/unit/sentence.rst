sentence
===================================

The Sentence module represents an entire CoNLL sentence. A sentence is composed of two main parts, the comments and the tokens. 

Comments
----------------------------------
Comments are treated as key-value pairs, where the separating character between key and value is ``=``. If there is no ``=`` present then then the comment is treated as a singleton and the corresponding value is ``None``. To access and write to these values look for values related to meta (the meta data of the sentence).

Some things to keep in mind is that the id and text of a sentence can be accessed through member properties directly rather than through method APIs. So ``sentence.id``, rather than ``sentence.meta_value('id')``. Note that since this API does not support changing the forms of tokens, and focuses on the annotation of tokens, the text value cannot be changed of a sentence, but all other meta values can be.

Tokens
----------------------------------
These are the meat of the sentence. Some things to note for tokens are that they can be accessed either through id as defined in the CoNLL data as a string or as numeric index. The string id indexing allows for multitoken and null nodes to be included easily. So the same indexing syntax understands both, ``sentence['2-3']`` and ``sentence[2]``.


API
----------------------------------
.. automodule:: pyconll.unit.sentence
    :members:
