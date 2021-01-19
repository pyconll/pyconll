load
===================================

This module defines the main interface to load CoNLL treebank resources. CoNLL treebanks can be loaded through a string or a file (or technically anything that can function as a string iterator). CoNLL resources can be loaded and held in memory, or simply iterated through a sentence at a time which is useful for handling very large files.

The fully qualified name of the module is ``pyconll.load``, but these methods are imported at the ``pyconll`` namespace level. This module provides the wrappers for loading from a string or file, but if another string iterator is available, for example, a network resource, this can be passed directly to the Conll_ constructor as well.

.. _Conll: unit/conll.html


Example
-----------------------------------
This example counts the number of times a token with a lemma of ``linguistic`` appeared in the treebank. If all the operations that will be done on the CoNLL file are readonly or are data aggregations, the ``iter_from`` alternatives are more memory efficient alternative as well. These methods will return an iterator over the sentences in the CoNLL resource rather than storing the CoNLL object in memory, which can be convenient when dealing with large files that do not need be completely loaded. This example uses the ``load_from_file`` method for illustration purposes.

::

    import pyconll

    example_treebank = '/home/myuser/englishdata.conll'
    conll = pyconll.load_from_file(example_treebank)

    count = 0
    for sentence in conll:
        for word in sentence:
            if word.lemma == 'linguistic':
                count += 1

    print(count)



API
----------------------------------
.. automodule:: pyconll.load
    :members:
