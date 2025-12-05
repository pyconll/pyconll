format
===================================

The ``format`` module defines the core interface for reading and writing tabular data formats. It provides three main classes: ``ReadFormat``, ``WriteFormat``, and ``Format`` (which inherits both).

Overview
----------------------------------

The Format system is built around the ``tokenspec`` decorator and the ``AbstractSentence`` ABC, allowing you to define custom token and sentence types and automatically generate optimized parsers and serializers for them. This makes ``pyconll`` flexible enough to work with CoNLL-U or any other tabular format.

The ``Format`` class compiles reading and writing logic based on your token schema at initialization time.

Classes
----------------------------------

ReadFormat[T, S]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides methods for parsing tabular data into Python objects. It provides operations for Tokens and Sentences, but most usage would be primarily on collections of Sentences.

WriteFormat[T, S]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides methods for serializing Python objects to tabular format. Like ReadFormat, it provides operations for Tokens and Sentences, but most usage would be primarily on collections of Sentences.

Format[T, S]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Combines both ``ReadFormat`` and ``WriteFormat`` functionality. This is the class you'll typically use. By separating out the read and write side future changes allowing for serialization or deserialization only types is possible.

Example
-----------------------------------

Creating a custom format for CoNLL-X:

.. code:: python

    from pyconll.format import Format
    from pyconll.schema import tokenspec, nullable, unique_array, field
    from pyconll.shared import Sentence
    from typing import Optional

    @tokenspec
    class TokenX:
        id: int
        form: str
        lemma: str
        cpostag: str
        postag: str
        feats: set[str] = field(unique_array(str, "|", "_"))
        head: int
        deprel: str
        phead: Optional[int] = field(nullable(int, "_"))
        pdeprel: Optional[str] = field(nullable(str, "_"))

    # Create format instance
    conllx = Format(TokenX, Sentence[TokenX], comment_marker="#", delimiter="\t")

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

For CoNLL-U specifically, use the pre-configured ``conllu`` or ``fast_conllu`` instance from ``pyconll.conllu`` rather than creating your own.

Advanced: Dynamic Field Descriptors
----------------------------------

The ``Format`` constructor accepts a ``field_descriptors`` parameter that allows you to provide field descriptors dynamically instead of as class attributes. This is useful for:

- Switching between different serialization strategies at runtime
- Performance tuning (e.g., using ``sys.intern`` for string interning)
- Sharing token classes across multiple formats

.. code:: python

    from pyconll.format import Format
    from pyconll.schema import tokenspec, nullable, via, FieldDescriptor
    from pyconll.shared import Sentence
    import sys
    from typing import Optional

    @tokenspec
    class Token:
        id: str
        form: str
        lemma: str
        upos: str

    # Define descriptors separately
    standard_descriptors: dict[str, Optional[FieldDescriptor]] = {
        'id': None,  # None for primitive types (str, int, float)
        'form': nullable(str, "_"),
        'lemma': nullable(str, "_"),
        'upos': nullable(str, "_"),
    }

    # Compact version using string interning for memory efficiency
    compact_descriptors: dict[str, Optional[FieldDescriptor]] = {
        'id': via(sys.intern),
        'form': nullable(via(sys.intern), "_"),
        'lemma': nullable(via(sys.intern), "_"),
        'upos': nullable(via(sys.intern), "_"),
    }

    # Create two different Format instances with the same Token class
    standard_format = Format(Token, Sentence[Token], field_descriptors=standard_descriptors)
    compact_format = Format(Token, Sentence[Token], field_descriptors=compact_descriptors)

When both class attributes (using ``field()``) and ``field_descriptors`` are provided, ``field_descriptors`` takes precedence. The ``extra_primitives`` parameter allows you to specify additional types that should be treated as primitives (constructed via their type constructor, serialized via ``str()``). This also takes precedence over anything provided on ``@tokenspec``. Note that one downside of the ``field_descriptors`` parameter is not that no type checking is performed, as opposed to using ``field()`` on the class definition, so this should be used with care and only in instances where the exact schema implementation will vary at runtime.

API
----------------------------------
.. automodule:: pyconll.format
    :members:
    :exclude-members: __dict__, __weakref__
