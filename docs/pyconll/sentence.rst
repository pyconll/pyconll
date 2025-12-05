sentence
===================================

The ``Sentence`` class defined in ``pyconll.shared`` represents a sentence across different formats. It inherits from ``AbstractSentence`` which describes the requirements for a sentence type. Most formats will have the same sentence structure, so one base case is given, but more advanced usage can be derived from a new class inheriting from ``AbstractSentence`` directly.

A ``Sentence`` is a simple container with two main components:

- ``meta: OrderedDict[str, Optional[str]]`` - Metadata/comments
- ``tokens: list[T]`` - List of token objects with the Sentence being generic to the exact token type.

There is a ``Sentence`` class defined in ``pyconll.conll`` which is built off of this base and adds the ``to_tree`` method.

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
    sent_id = sentence.meta['sent_id']
    text = sentence.meta['text']

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

Tokens
----------------------------------
Tokens are stored as a simple list. The type of tokens depends on the exact token specification provided when parsing.

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

API
----------------------------------
.. automodule:: pyconll.sentence
    :members:
    :exclude-members: __dict__, __weakref__
