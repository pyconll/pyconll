Getting Started
===================================

Overview
----------------------------------

``pyconll`` is a low level wrapper around the CoNLL-U format. This document explains how to quickly get started loading and manipulating CoNLL-U files within ``pyconll``, and will go through a typical end-to-end scenario.

To install the library, run ``pip install pyconll`` from your python enlistment.

Loading CoNLL-U
----------------------------------

To start, a CoNLL-U resource must be loaded, and ``pyconll`` can load from files, urls, and strings. Specific API information can be found in the load_ module documentation. Below is a typical example of loading a file on the local computer.

.. _load: pyconll/load.html

.. code:: python

    import pyconll

    my_conll_file_location = './ud/train.conll'
    train = pyconll.load_from_file(my_conll_file_location)

Loading methods usually return a ``Conll`` object, but some methods return an iterator over ``Sentences`` and do not load the entire ``Conll`` object into memory at once.

Traversing CoNLL-U
----------------------------------

After loading a CoNLL-U file, we can traverse the CoNLL-U structure; ``Conll`` objects wrap ``Sentences`` and ``Sentences`` wrap ``Token``. Here is what traversal normally looks like.

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

Note that most objects in ``pyconll`` are mutable, except for a select few fields, so changing the ``Token`` object remains with the ``Sentence``.

Outputting CoNLL-U
----------------------------------

Once you are done working with a ``Conll`` object, you may need to output your results. The object can be serialized back into the CoNLL-U format, through the ``conll`` method. ``Conll``, ``Sentence``, and ``Token`` objects are all ``Conllable`` which means they have a corresponding ``conll`` method which serializes the objects into the appropriate string representation.


Conclusion
----------------------------------

``pyconll`` allows for easy CoNLL-U loading, traversal, and serialization. Developers can define their own transformation or analysis of the loaded CoNLL-U data, and pyconll handles all the parsing and serialization logic. There are still some parts of the library that are not covered here such as the ``Tree`` data structure, loading files from network, and error handling, but the information on this page will get developers through the most important use cases.
