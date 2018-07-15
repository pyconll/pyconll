load
===================================

This is the main module you should interface with if wanting to load an entire CoNLL file, rather than individual sentences which should be less common. The API allows for loading CoNLL data from a string or from a file, and allows for iteration over the data, rather than storing a large CoNLL object in memory if so desired.

Note that the fully qualified name is ``pyconll.load``, but these methods can also be accessed using the ``pyconll`` namespace.


Example
-----------------------------------
This example counts the number of times a token with a lemma of ``linguistic`` appeared in the treebank. Note that if all the operations that will be done on the CoNLL file are readonly, consider using the ``iter_from`` alternatives. These methods will return an iterator over each sentence in the CoNLL file rather than storing an entire CoNLL object in memory, which can be convenient when dealing with large files that do not need to persist.

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



API Reference
-----------------------------------


.. automodule:: pyconll.load
    :members:
