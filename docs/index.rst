pyconll
===================================

Welcome to the ``pyconll`` documentation homepage.

pyconll is designed as a flexible wrapper around the CoNLL-U format (and other tabular formats), to allow for easy loading and manipulating of dependency annotations. See an example of pyconll's syntax below.

.. code:: python

   from pyconll.conllu import conllu

   # Load from disk into memory and iterate over the corpus, printing
   # sentence ids, and capturing unique verbs
   verbs = set()
   corpus = conllu.load_from_file('ud-english-train.conllu')
   for sentence in corpus:
      print(sentence.meta.get('sent_id'))
      for token in sentence.tokens:
         if token.upos == 'VERB':
            verbs.add(token.lemma)

   # Use the iterate version over a larger corpus to save memory
   huge_corpus_iter = conllu.iter_from_file('annotated_shakespeare.conllu')
   for sentence in huge_corpus_iter:
      print(sentence.meta.get('sent_id'))


Those new to the project should visit the `Getting Started`__ page which goes through an end-to-end example using pyconll. For loading files visit the format_ page. For API usage, confer with the sentence_, token_, and schema_ module pages which contain documentation for the base data types. Module documentation, guidance pages, and more are listed below in the table of contents.

For more information, the github_ project page has examples, tests, and source code.

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :titlesonly:

   Getting Started <starting>
   Migration Guide <migration>
   Custom Formats <custom>
   README <readme>
   CHANGELOG <changelog>
   pyconll/conllu
   pyconll/exception
   pyconll/format
   pyconll/schema
   pyconll/sentence
   pyconll/token
   pyconll/tree


.. _github: https://github.com/matgrioni/pyconll/
.. _format: pyconll/format.html
.. _schema: pyconll/schema.html
.. _conllu: pyconll/conllu.html
.. _sentence: pyconll/unit/sentence.html
.. _token: pyconll/unit/token.html
__ starting.html
