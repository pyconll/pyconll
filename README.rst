|Build Status| |Coverage Status| |Documentation Status|

pyconll
-------

*Easily work with **CoNLL** files using the familiar syntax of
**python**.*

The current version is 2.0.0. This version is fully functional, stable,
tested, documented, and actively developed.

Links
'''''

-  `Homepage <https://pyconll.github.io>`__
-  `Documentation <https://pyconll.readthedocs.io/>`__

Installation
~~~~~~~~~~~~

As with most python packages, simply use ``pip`` to install from PyPi.

::

    pip install pyconll

This package is designed for, and only tested with python 3.4 and up and
will not be backported to python 2.x.

Motivation
~~~~~~~~~~

This tool is intended to be a **minimal**, **low level**, and
**functional** library in a widely used programming language.
``pyconll`` creates a thin API on top of raw CoNLL annotations that is
simple and intuitive in a popular language that can be used as building
block in a complex system or the engine in small one off scripts.

After working with the UD project, I realized there is a dissapointing
lack of low level APIs for working with the Universal Dependencies
project. Current tooling focuses on graph transformations and DSLs for
automated manipulation of CoNLL-U files. Tools such as
`Grew <http://grew.fr/>`__ and `Treex <http://ufal.mff.cuni.cz/treex>`__
are very powerful and productive, but have a learning curve and are
limited in what their DSL's can represent. On the other hand,
`CL-CoNLLU <https://github.com/own-pt/cl-conllu/>`__ is simple and low
level, but Common Lisp is not widely used in NLP.
`UDAPI <http://udapi.github.io/>`__ is in python but it is very large
and how little guidance on usage. ``pyconll`` attempts to fill in the
gap between what these other projects have accomplished.

Other useful tools can be found on the Universal Dependencies
`website <https://universaldependencies.org/tools.html>`__.

Hopefully, individual researchers will find use in this project, and
will use it as a building block for more popular tools. By using
``pyconll``, researchers gain a standardized and feature rich base on
which they can build larger projects and without worrying about CoNLL
annotation and output. ``pyconll``

Code Snippet
~~~~~~~~~~~~

.. code:: python

    # This snippet finds what lemmas are marked as AUX which is a closed class POS in UD
    import pyconll

    UD_ENGLISH_TRAIN = './ud/train.conll'

    train = pyconll.load_from_file(UD_ENGLISH_TRAIN)

    aux_lemmas = set()
    for sentence in train:
        for token in sentence:
            aux_lemmas.add(token.lemma)

Uses and Limitations
~~~~~~~~~~~~~~~~~~~~

This package edits CoNLL-U annotations. This does not include the
annotated text itself. Word forms on Tokens are not editable and
Sentence Tokens cannot be reassigned or reordered. ``pyconll`` focuses
on editing CoNLL-U annotation rather than creating it or changing the
underlying text that is annotated. If there is interest in this
functionality area, please create a github issue for more visibility.

Contributing
~~~~~~~~~~~~

Contributions to this project are welcome and encouraged! If you are
unsure how to contribute, here is a
`guide <https://help.github.com/en/articles/creating-a-pull-request-from-a-fork>`__
from Github explaining the basic workflow. After cloning this repo,
please run ``make hooks`` and ``pip install -r requirements.txt`` to
properly setup locally. ``make hooks`` setups up a pre-push hook to
validate that code matches the default YAPF style. While this is
technically optional, it is highly encouraged.
``pip install -r requirements.txt`` sets up environment dependencies
like ``yapf``, ``twine``, ``sphinx``, etc.

README and CHANGELOG
''''''''''''''''''''

When changing either of these files, please change the Markdown version
and run ``make docs`` so that the other versions stay in sync.

Code Formatting
'''''''''''''''

Code formatting is done automatically on push if githooks are setup
properly. The code formatter is
`YAPF <https://github.com/google/yapf>`__, and using this ensures that
coding style stays consistent over time and between authors.

.. |Build Status| image:: https://travis-ci.org/pyconll/pyconll.svg?branch=master
   :target: https://travis-ci.org/pyconll/pyconll
.. |Coverage Status| image:: https://coveralls.io/repos/github/pyconll/pyconll/badge.svg?branch=master
   :target: https://coveralls.io/github/pyconll/pyconll?branch=master
.. |Documentation Status| image:: https://readthedocs.org/projects/pyconll/badge/?version=latest
   :target: https://pyconll.readthedocs.io/en/latest/?badge=latest
