Getting Started
===================================

Overview
----------------------------------

``pyconll`` is a low level wrapper around the CoNLL-U format (and other tabular formats). This document explains how to quickly get started loading and manipulating CoNLL-U files within ``pyconll``, and will go through a typical end-to-end scenario.

To install the library, run ``pip install pyconll`` from your python enlistment.

Loading CoNLL-U
----------------------------------

To start, a CoNLL-U resource must be loaded. The ``pyconll.conllu`` module provides a pre-configured ``Format`` instance called ``conllu`` that can load from files and strings. Below is a typical example of loading a file on the local computer.

.. code:: python

    from pyconll.conllu import conllu

    my_conll_file_location = './ud/train.conllu'
    train = conllu.load_from_file(my_conll_file_location)

Loading methods return a ``list[Sentence]``. Some methods like ``iter_from_file`` return an iterator over ``Sentence`` and do not load the entire corpus into memory at once, which is useful for very large files and also faster due to reduced memory pressure.

Traversing CoNLL-U
----------------------------------

After loading a CoNLL-U file, we can traverse the corpus. The loaded data is a list of Sentences, and each Sentence_ contains tokens. Here is what traversal normally looks like.

.. code:: python

    for sentence in train:
        for token in sentence.tokens:
            # Do work within loops
            pass

Statistics such as lemmas for a certain closed class POS or number of non-projective punctuation dependencies can be computed through these loops. As an abstract example, we have defined some predicate, ``sentence_pred``, and some transformation of noun tokens, ``noun_token_transformation``, and  we wish to transform all nouns in sentences that match our predicate, we can write the following.

.. code:: python

    for sentence in train:
        if sentence_pred(sentence):
            for token in sentence.tokens:
                if token.upos == 'NOUN':
                    noun_token_transformation(token)

Note that objects in ``pyconll`` are mutable, so changes are possible on the ``Token`` or ``Sentence`` objects and can be serialized out again to a CoNLL-U file when processing is complete.

Outputting CoNLL-U
----------------------------------

Once you are done working with your corpus, you may need to output your results. The ``WriteFormat`` class (which ``conllu`` is an instance of) provides serialization methods. You can serialize individual tokens or sentences, or write an entire corpus to a file.

When creating the file to write to, remember that CoNLL-U is UTF-8 encoded.

.. code:: python

    from pyconll.conllu import conllu

    # Serialize individual items
    token_string = conllu.serialize_token(token)
    sentence_string = conllu.serialize_sentence(sentence)

    # Write entire corpus to file (most efficient)
    with open('output.conllu', 'w', encoding='utf-8') as f:
        conllu.write_corpus(train, f)

Complete example
----------------------------------

Putting together all the above elements, a complete example from loading, to transformation, to output looks as follows.

.. code:: python

    from pyconll.conllu import conllu

    # Load file
    my_conll_file_location = './ud/train.conllu'
    train = conllu.load_from_file(my_conll_file_location)

    # Process and transform
    for sentence in train:
        if sentence_pred(sentence):
            for token in sentence.tokens:
                if token.upos == 'NOUN':
                    noun_token_transformation(token)

    # Output changes. This writes directly to file.
    with open('output.conllu', 'w', encoding='utf-8') as f:
        conllu.write_corpus(train, f)

Conclusion
----------------------------------

``pyconll`` allows for easy CoNLL-U loading, traversal, and serialization. Developers can define their own transformation or analysis of the loaded CoNLL-U data, and pyconll handles all the parsing and serialization logic. There are still some parts of the library that are not covered here such as the ``Tree`` data structure, custom token schemas, and error handling, but the information on this page will get developers through the most important use cases.

.. _Sentence: pyconll/unit/sentence.html
.. _Tokens: pyconll/unit/token.html