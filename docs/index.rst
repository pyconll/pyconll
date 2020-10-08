pyconll
===================================

Welcome to the ``pyconll`` documentation homepage.

pyconll is designed as a flexible wrapper around the CoNLL-U format, for easy loading and manipulating of dependency annotations.

.. code:: python

   import pyconll

   # Load from disk into memory and iterate over it, printing sentence ids,
   # and capturing unique verbs
   verbs = set()
   corpus = pyconll.load_from_file('ud-english-train.conllu')
   for sentence in corpus:
      print(sentence.id)
      for token in sentence:
         if token.upos == 'VERB':
            verbs.add(token.lemma)

   # Iterate over a corpus to save memory and for larger files.
   huge_corpus_iter = pyconll.iter_from_file('annotated_shakespeare.conllu')
   for sentence in huge_corpus_iter:
      print(sentence.id)


Module documentation, changelogs, and guidance pages are listed below in the table of contents. Those new to the project should visit the `Getting Started`__ page which goes through an end-to-end example of using pyconll. Other useful pages include the load_, conll_, sentence_, and token_ pages which contain documentation for the base CoNLL-U data types.

For more information, the github_ project page has examples, tests, and source code.

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :titlesonly:

   Getting Started <starting>

   pyconll/load
   pyconll/unit/token
   pyconll/unit/sentence
   pyconll/unit/conll
   pyconll/tree/tree
   pyconll/util
   pyconll/conllable
   pyconll/exception

   README <readme>
   CHANGELOG


.. _github: https://github.com/matgrioni/pyconll/
.. _load: load.html
.. _conll: conll.html
.. _sentence: sentence.html
.. _token: token.html
__ starting.html
