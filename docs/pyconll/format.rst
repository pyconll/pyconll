format
===================================

The ``format`` module defines the core interface for reading and writing tabular data formats. It provides three main classes: ``ReadFormat``, ``WriteFormat``, and ``Format`` (which inherits both).

Overview
----------------------------------

The Format system is built around the ``TokenSchema`` protocol, allowing you to define custom token types and automatically generate optimized parsers and serializers for them. This makes ``pyconll`` flexible enough to work with CoNLL-U or any other tabular format.

The ``Format`` class compiles reading and writing logic based on your token schema at initialization time.

Classes
----------------------------------

ReadFormat[T]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides methods for parsing tabular data into Python objects. It provides operations for Tokens and Sentences, but most usage would be primarily on collections of Sentences.

WriteFormat[T]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides methods for serializing Python objects to tabular format. Like ReadFormat, it provides operations for Tokens and Sentences, but most usage would be primarily on collections of Sentences.

Format[T]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Combines both ``ReadFormat`` and ``WriteFormat`` functionality. This is the class you'll typically use. By separating out the read and write side future changes allowing for serialization or deserialization only types is possible.

Example
-----------------------------------

Creating a custom format for CoNLL-X:

.. code:: python

    from pyconll.format import Format
    from pyconll.schema import TokenSchema, nullable, unique_array

    class TokenX(TokenSchema):
        id: int
        form: str
        lemma: str
        cpostag: str
        postag: str
        feats: set[str] = unique_array(str, "|", "_")
        head: int
        deprel: str
        phead: Optional[int] = nullable(int, "_")
        pdeprel: Optional[str] = nullable(str, "_")

    # Create format instance
    conllx = Format(TokenX, comment_marker="#", delimiter="\\t")

    # Load data
    sentences = conllx.load_from_file("data.conllx")

    # Modify data
    for sentence in sentences:
        for token in sentence.tokens:
            if token.postag == "NN":
                token.feats.add("Modified")

    # Write back
    with open("output.conllx", "w") as f:
        conllx.write_corpus(sentences, f)

Using the pre-configured CoNLL-U format:

.. code:: python

    from pyconll.conllu import conllu  # Pre-defined Format instance

    # Load
    sentences = conllu.load_from_file("train.conllu")

    # Stream for large files
    for sentence in conllu.iter_from_file("huge.conllu"):
        process(sentence)

Performance Notes
----------------------------------

The Format class uses dynamic code generation (via Python's ``compile()`` and ``exec()``) to create optimized parsers and serializers. This compilation happens once at Format initialization, so:

- Creating a Format instance has some overhead (typically milliseconds).
- Once created, parsing and serialization are optimized and cached.
- Reuse Format instances rather than recreating them.

For CoNLL-U specifically, use the pre-configured ``conllu`` instance from ``pyconll.conllu`` rather than creating your own.

API
----------------------------------
.. automodule:: pyconll.format
    :members:
    :exclude-members: __dict__, __weakref__
