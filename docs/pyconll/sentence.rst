sentence
===================================

The ``Sentence`` module represents an entire CoNLL sentence, which is composed of metadata (comments) and tokens.

A ``Sentence`` is a simple container with two main components:

- ``meta: OrderedDict[str, Optional[str]]`` - Metadata/comments
- ``tokens: list[T]`` - List of token objects (type depends on the schema used)

Metadata
----------------------------------
Metadata (comments in the CoNLL-U file) are stored as an ordered dictionary. Comments are treated as key-value pairs, separated by the ``=`` character. A singleton comment has no ``=`` present; in this situation the key is the comment string, and the value is ``None``.

Accessing Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from pyconll.conllu import conllu

    sentences = conllu.load_from_file('train.conllu')
    sentence = sentences[0]

    # Access metadata
    sent_id = sentence.meta.get('sent_id')
    text = sentence.meta.get('text')

    # Add new metadata
    sentence.meta['custom'] = 'value'

    # Singleton metadata
    sentence.meta['newpar'] = None

Common Metadata Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In CoNLL-U, common metadata keys include:

- ``sent_id`` - Sentence identifier
- ``text`` - The original sentence text
- ``newdoc id`` - Document boundary marker
- ``newpar id`` - Paragraph boundary marker
- ``sent_id`` - Sentence identifier

Tokens
----------------------------------
Tokens are stored as a simple list. The type of tokens depends on the ``TokenSchema`` used when parsing.

For CoNLL-U files, tokens are of type ``Token`` from ``pyconll.conllu``.

Accessing Tokens
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from pyconll.conllu import conllu

    sentences = conllu.load_from_file('train.conllu')
    sentence = sentences[0]

    # Iterate over tokens
    for token in sentence.tokens:
        print(token.form, token.upos)

    # Access by index
    first_token = sentence.tokens[0]

    # Build ID index if needed
    token_by_id = {t.id: t for t in sentence.tokens}
    token = token_by_id['5']

Version 4.0 Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
    **Version 4.0** simplified the Sentence structure:

    - Tokens are now accessed via ``sentence.tokens`` (a list)
    - Token ID indexing (e.g., ``sentence['5']``) is no longer supported
    - Build your own index if you need ID-based lookup: ``{t.id: t for t in sentence.tokens}``
    - Metadata is accessed via ``sentence.meta`` (an OrderedDict)
    - ``sentence.id`` and ``sentence.text`` properties were removed; use ``sentence.meta.get('sent_id')`` and ``sentence.meta.get('text')``

Example Usage
----------------------------------

.. code:: python

    from pyconll.conllu import conllu

    # Load sentences
    sentences = conllu.load_from_file('train.conllu')

    for sentence in sentences:
        # Access metadata
        print(f"Processing sentence: {sentence.meta.get('sent_id')}")

        # Build token index for dependency lookups
        token_by_id = {t.id: t for t in sentence.tokens}

        # Process tokens
        for token in sentence.tokens:
            if token.upos == 'VERB':
                # Look up head
                if token.head and token.head != '0':
                    head = token_by_id.get(token.head)
                    if head:
                        print(f"{token.form} -> {head.form}")

        # Modify metadata
        sentence.meta['analyzed'] = 'true'

    # Write back
    with open('output.conllu', 'w') as f:
        conllu.write_corpus(sentences, f)

API
----------------------------------
.. automodule:: pyconll.sentence
    :members:
    :exclude-members: __dict__, __weakref__
