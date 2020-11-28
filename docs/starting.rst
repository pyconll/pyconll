Getting Started
===================================

Overview
----------------------------------

``pyconll`` is a low level wrapper around the CoNLL-U format. This document explains how to quickly get started loading and manipulating CoNLL-U files within ``pyconll``, and will go through a typical end-to-end scenario.

To install the library, run ``pip install pyconll`` from your python enlistment.

Loading CoNLL-U
----------------------------------

To start, a CoNLL-U resource must be loaded, and ``pyconll`` can load_ from files, urls, and strings. Specific API information can be found in the load_ module documentation. Below is a typical example of loading a file on the local computer.

.. code:: python

    import pyconll

    my_conll_file_location = './ud/train.conll'
    train = pyconll.load_from_file(my_conll_file_location)

Loading methods usually return a ``Conll`` object, but some methods return an iterator over ``Sentences`` and do not load the entire ``Conll`` object into memory at once. The ``Conll`` object satisfies the MutableSequence_ contract in python, which means it functions nearly the same as a `list`.

Traversing CoNLL-U
----------------------------------

After loading a CoNLL-U file, we can traverse the Conll_ structure. Conll_ objects wrap Sentences_ and Sentences_ wrap Tokens_. Here is what traversal normally looks like.

.. code:: python

    for sentence in train:
        for token in sentence:
            # Do work within loops
            pass

Statistics such as lemmas for a certain closed class POS or number of non-projective punctuation dependencies can be computed through these loops. As an abstract example, we have defined some predicate, ``sentence_pred``, and some transformation of noun tokens, ``noun_token_transformation``, and  we wish to transform all nouns in sentences that match our predicate, we can write the following.

.. code:: python

    for sentence in train:
        if sentence_pred(sentence):
            for token in sentence:
                if token.pos == 'NOUN':
                    noun_token_transformation(token)

Note that most objects in ``pyconll`` are mutable, except for a select few fields, so changes on the ``Token`` object remain with the ``Sentence`` and can be output back into CoNLL format when processing is complete.

Outputting CoNLL-U
----------------------------------

Once you are done working with a ``Conll`` object, you may need to output your results. The object can be serialized back into the CoNLL-U format, through the ``conll`` method. ``Conll``, ``Sentence``, and ``Token`` objects are all Conllable_ which means they have a corresponding ``conll`` method which serializes the objects into the appropriate string representation.

A more efficient way of outputting an entire Conll file would be to use the ``write`` method, which prevents creating the entire Conll file string in memory. Remember that, CoNLL-U is UTF-8 encoded.

Complete example
----------------------------------

Putting together all the above elements, a complete example from loading, to transformation, to output looks as follows.

.. code:: python

    import pyconll

    # Load file
    my_conll_file_location = './ud/train.conll'
    train = pyconll.load_from_file(my_conll_file_location)

    # Process and transform
    for sentence in train:
        if sentence_pred(sentence):
            for token in sentence:
                if token.pos == 'NOUN':
                    noun_token_transformation(token)

    # Output changes. This writes directly to file, an alternative is to use
    # train.conll() which will return the entire output string at once.
    with open('output.conllu', 'w', encoding='utf-8') as f:
        train.write(f)

Conclusion
----------------------------------

``pyconll`` allows for easy CoNLL-U loading, traversal, and serialization. Developers can define their own transformation or analysis of the loaded CoNLL-U data, and pyconll handles all the parsing and serialization logic. There are still some parts of the library that are not covered here such as the ``Tree`` data structure, loading files from network, and error handling, but the information on this page will get developers through the most important use cases.

.. _MutableSequence: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSequence
.. _load: pyconll/load.html
.. _Conll: pyconll/unit/conll.html
.. _Sentences: pyconll/unit/sentence.html
.. _Tokens: pyconll/unit/token.html
.. _Conllable: pyconll/conllable.html