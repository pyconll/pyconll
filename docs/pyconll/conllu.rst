conllu
===================================

The ``conllu`` module provides the standard CoNLL-U format implementation, including the ``Token`` and ``Sentence`` class and pre-configured ``Format`` instance for reading and writing CoNLL-U files.

Overview
----------------------------------

This module is the primary entry point for working with CoNLL-U files. It provides:

- ``Token`` - The CoNLL-U token schema with all standard fields.
- ``Sentence`` - The CoNLL-U sentence schema which can create a Tree model and provides access to metadata and tokens.
- ``conllu`` - A pre-configured ``Format`` instance for CoNLL-U. This should be the default in most use cases as opposed to ``fast_conllu``.
- ``fast_conllu`` - A pre-configured ``Format`` instance for CoNLL-U which trades off parser speed for increased memory usage.
- ``ConllFormat`` which provides a type alias to abstract from having to use the full types of ``conllu`` and ``fast_conllu``.

The ``conllu`` Format Instance
----------------------------------

The module exports pre-configured ``Format[Token]`` instances named ``conllu`` and ``fast_conllu`` that are ready to use and are completely interchangeable.

.. code:: python

    from pyconll.conllu import conllu, ConlluFormat

    cformat: ConlluFormat = conllu # or conllu.fast_conllu

    # Load entire file into memory
    sentences = cformat.load_from_file('train.conllu')

    # Stream large files
    for sentence in cformat.iter_from_file('huge.conllu'):
        process(sentence)

    # Parse from string
    text = """# sent_id = 1
    1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
    2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\tSpaceAfter=No

    """
    sentences = cformat.load_from_string(text)

    # Write back to file
    with open('output.conllu', 'w') as f:
        cformat.write_corpus(sentences, f)

The Token Class
----------------------------------

The ``Token`` class defines the CoNLL-U format with 10 standard columns:

Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. ``id: str`` - Token ID (e.g., "1", "2-3", "2.1")
2. ``form: Optional[str]`` - Word form or punctuation symbol
3. ``lemma: Optional[str]`` - Lemma or stem
4. ``upos: Optional[str]`` - Universal part-of-speech tag
5. ``xpos: Optional[str]`` - Language-specific part-of-speech tag
6. ``feats: dict[str, set[str]]`` - Morphological features
7. ``head: Optional[str]`` - Head token ID
8. ``deprel: Optional[str]`` - Dependency relation
9. ``deps: dict[str, tuple[str, ...]]`` - Enhanced dependencies
10. ``misc: dict[str, Optional[set[str]]]`` - Miscellaneous annotations

Example Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from pyconll.conllu import conllu

    sentences = conllu.load_from_file('train.conllu')

    for sentence in sentences:
        for token in sentence.tokens:
            # Access basic fields
            if token.upos == 'VERB':
                print(f"Verb: {token.form} -> {token.lemma}")

            # Modify features
            if token.upos == 'NOUN':
                if 'Number' not in token.feats:
                    token.feats['Number'] = set()
                token.feats['Number'].add('Sing')

            # Add misc annotations
            token.misc['Analyzed'] = None  # Singleton feature

    # Write modified corpus
    with open('output.conllu', 'w') as f:
        conllu.write_corpus(sentences, f)

Dictionary Fields
----------------------------------

Three fields (``feats``, ``deps``, ``misc``) are dictionaries.

feats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Morphological features as key-value pairs:

.. code:: python

    # Example: Gender=Fem|Number=Sing
    token.feats = {
        'Gender': {'Fem'},
        'Number': {'Sing'}
    }

    # Modify
    token.feats['Case'] = {'Nom'}
    token.feats['Number'].add('Plur')  # Now {'Sing', 'Plur'}

    # Serializes to: Case=Nom|Gender=Fem|Number=Sing,Plur

deps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Enhanced dependencies as head-to-relation mappings:

.. code:: python

    # Example: 4:nsubj
    token.deps = {
        '4': ('nsubj',)
    }

    # The tuple is a fixed size per element but can vary between elements.
    # In CoNLL-U, there is usually only two elements in this field.

misc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Miscellaneous annotations with optional values:

.. code:: python

    # Singleton features (no value)
    token.misc['SpaceAfter'] = None  # Serializes as "SpaceAfter"

    # Features with values
    token.misc['Translit'] = {'example'}  # Serializes as "Translit=example"

    # Multiple values
    token.misc['Gloss'] = {'cat', 'feline'}  # Serializes as "Gloss=cat,feline"

API
----------------------------------
.. automodule:: pyconll.conllu
    :members:
    :exclude-members: __dict__, __weakref__
