Getting Started
===================================

Overview
----------------------------------

``pyconll`` is a low level wrapper around the CoNLL-U format. Getting started should be straight forward using a python 3 environment. This document will explain how to quickly get started loading and manipulating CoNLL-U files using this format. This document will go through a typical end-to-end example.

To install the library simply run, ``pip install pyconll``. This is all you need to start using the library on your local python enlistment.

Loading CoNLL-U
----------------------------------

The first thing that needs to be done is load a CoNLL-U resource. ``pyconll`` allows for loading of resources of different kinds, such as files, network files, strings, and ``Sentence`` iterables. More specific information can be found in the load module documentation. Below is the typical example of loading a file on the local computer


.. code:: python

    import pyconll

    my_conll_file_location = './ud/train.conll'
    train = pyconll.load_from_file(my_conll_file_location)

All loading methods provide back a ``Conll`` object, except for the methods that return a ``Sentence`` iterator.

Traversing CoNLL-U
----------------------------------

After loading a CoNLL-U file the next step would be to traverse through the contents of the CoNLL-U object. This can be done at the ``Sentence`` level, and from there, at the ``Token`` level. During traversal, statistics may be computed, sentences transformed, etc. Here is what traversal looks like.

.. code:: python

    for sentence in train:
        for token in sentence:
            # Do work within loops
            pass

Statistics that may be computed include lemma occurrences for a certain POS, especially for closed class POS, or checking for the presence of sentence end punctuation that does not attach to the sentence root. As an abstract example, we have defined some predicate, ``sentence_pred``, and some transformation of noun tokens, ``noun_token_transformation``. If we wish to transform all nouns in sentences that match our predicate, we can write the following.

.. code:: python

    for sentence in train:
        if sentence_pred(sentence):
            for token in sentence:
                if token.pos == 'NOUN':
                    noun_token_transformation(token)

Note that Conll objects in general in ``pyconll`` are mutable, except for a select few fields, and so the ``Token`` objects seen while traversing are the same ``Token`` objects that are in the ``Sentence``, and any changes will be reflected in both code paths.

Outputting CoNLL-U
----------------------------------

Finally, once you are done transforming a ``Conll`` object, the object can be serialized back into the CoNLL-U format. Following our example, this is done through, ``train.conll()``. ``Conll``, ``Sentence``, and ``Token`` objects are all ``Conllable`` which means they have a corresponding ``conll`` method which serializes the objects contents appropriately according to the CoNLL-U format.


Conclusion
----------------------------------

``pyconll`` allows for easy CoNLL-U loading, traversal, and serialization. Developers still need to define their own logic for linguistic interpretation of the data in the CoNLL-U format, but working with the format is much more pleasing if you can worry about less. There are still some parts of the library that are not covered here such as ``SentenceTree``, loading files from network, and error handling, but this information get developers through the most important use cases.
