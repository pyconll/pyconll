sentence
===================================

The ``Sentence`` module represents an entire CoNLL sentence, which is composed of comments and tokens.

Comments
----------------------------------
Comments are treated as key-value pairs, separated by the ``=`` character. A singleton comment has no ``=`` present. In this situation the key is the comment string, and the value is ``None``. Methods for reading and writing cmoments on Sentences are prefixed with ``meta_``, and are found below.

For convenience, the id and text comments are accessible through member properties on the Sentence in addition to metadata methods. So ``sentence.id`` and ``sentence.meta_value('id')`` are equivalent but the former is more concise and readable. Since this API does not support changing a token's form, the ``text`` comment cannot be changed. Text translations or transliterations can still be added just like any other comment.

Document and Paragraph ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In previous versions of pyconll, the document and paragraph id of a Sentence were extracted similar to text and id information. This causes strange results and semantics when adding Sentences to a Conll object since the added sentence may have a ``newpar`` or ``newdoc`` comment which affects all subsequent Sentence ids. For simplicity's sake, this information is now only directly available as normal metadata information.

Tokens
----------------------------------
This is the heart of the sentence. Tokens can be indexed on Sentences through their id value, as a string, or as a numeric index. So all of the following calls are valid, ``sentence['5']``, ``sentence['2-3']``, ``sentence['2.1']``, and ``sentence[2]``. Note that ``sentence[x]`` and ``sentence[str(x)]`` are not interchangeable. These calls are both valid but have different meanings.


API
----------------------------------
.. automodule:: pyconll.unit.sentence
    :members:
    :exclude-members: __dict__, __weakref__
