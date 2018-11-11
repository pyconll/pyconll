load
===================================

This is the main module to interface with to load an entire CoNLL treebank resources. The module defines methods for loading a CoNLL treebank through a string, file, or network. There also exist methods that iterate over the CoNLL resource data rather than storing the large CoNLL object in memory, if so desired.

Note that the fully qualified name is ``pyconll.load``, but these methods can also be accessed using the ``pyconll`` namespace.


Example
-----------------------------------
This example counts the number of times a token with a lemma of ``linguistic`` appeared in the treebank. If all the operations that will be done on the CoNLL file are readonly or are data aggregations, the ``iter_from`` alternatives are more efficient and recommended. These methods will return an iterator over the sentences in the CoNLL resource rather than storing the CoNLL object in memory, which can be convenient when dealing with large files that do not need be completely loaded.

::

    import pyconll

    example_treebank = '/home/myuser/englishdata.conll'
    conll = pyconll.iter_from_file(example_treebank)

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
