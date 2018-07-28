|Build Status| |Coverage Status| |Documentation Status|

pyconll
-------

*Easily work with **CoNLL** files using the familiar syntax of
**python**.*

The current version is 0.3. This version is fully functional, stable,
tested, documented, and actively developed.

Links
'''''

-  `Homepage <https://pyconll.github.io>`__
-  `Documentation <https://pyconll.readthedocs.io/>`__

Motivation
~~~~~~~~~~

When working with the Universal Dependencies project, there are a
dissapointing lack of low level APIs. There are many great tools, but
few are general purpose enough. Grew is a great tool, but it is slightly
limiting for some tasks (and extremely productive for others). Treex is
similar to Grew in this regard. CL-CoNLLU is a good tool in this regard,
but it is written in a language that many are not familiar with, Common
Lisp. UDAPI might fit the bill with its python API, but the package
itself is quite large and the documentation impossible to get through.
Various more tools can be found on the Universal Dependencies website
and all are very nice pieces of software, but most of them are lacking
in this desired usage pattern. ``pyconll`` creates a thin API on top of
raw CoNLL annotations that is simple and intuitive. This is an attempt
at a small, minimal, and intuitive package in a popular language that
can be used as building block in a complex system or the engine in small
one off scripts.

Hopefully, individual researchers will find use in this project, and
will use it as a building block for more popular tools. By using
``pyconll``, researchers gain a standardized and feature rich base on
which they can build larger projects and not worry about CoNLL
annotation and output.

Code Snippet
~~~~~~~~~~~~

.. code:: python

    import pyconll

    UD_ENGLISH_TRAIN = './ud/train.conll'

    train = pyconll.load_from_file(UD_ENGLISH_TRAIN)

    for sentence in train:
        for token in sentence:
            # Do work here.
            if token.form == 'Spain':
                token.upos = 'PROPN'

More examples can be found in the ``examples`` folder.

Uses and Limitations
~~~~~~~~~~~~~~~~~~~~

The usage of this package is to enable editing of CoNLL-U format
annotations of sentences. Note that this does not include the actual
text that is annotated. For this reason, word forms for Tokens are not
editable and Sentence Tokens cannot be reassigned. Right now, this
package seeks to allow for straight forward editing of annotation in the
CoNLL-U format and does not include changing tokenization or creating
completely new Sentences from scratch. If there is interest in this
feature, it can be revisted for more evaluation.

Installation
~~~~~~~~~~~~

As with most python packages, simply use ``pip`` to install from PyPi.

::

    pip install pyconll

This package is designed for, and only tested with python 3.4 and above.
Backporting to python 2.7 is not in future plans.

Documentation
~~~~~~~~~~~~~

The full API documentation can be found online at
https://pyconll.readthedocs.io/. A growing number of examples can be
found in the ``examples`` folder.

Contributing
~~~~~~~~~~~~

If you would like to contribute to this project you know the drill.
Either create an issue and wait for me to repond and fix it or ignore
it, or create a pull request or both. When cloning this repo, please run
``make hooks`` and ``pip install -r requirements.txt`` to properly setup
the repo. ``make hooks`` setups up the pre-push hook, which ensures the
code you push is formatted according to the default YAPF style.
``pip install -r requirements.txt`` simply sets up the environment with
dependencies like ``yapf``, ``twine``, ``sphinx``, and so on.

README and CHANGELOG
^^^^^^^^^^^^^^^^^^^^

When changing either of these files, please run ``make docs`` so that
the ``.rst`` versions stay in sync. The main version is the markdown
version.

Code Formatting
^^^^^^^^^^^^^^^

Code formatting is done automatically on push if githooks are setup
properly. The code formatter is YAPF, and using this ensures that new
code stays in the same style.

.. |Build Status| image:: https://travis-ci.org/pyconll/pyconll.svg?branch=master
   :target: https://travis-ci.org/pyconll/pyconll
.. |Coverage Status| image:: https://coveralls.io/repos/github/pyconll/pyconll/badge.svg?branch=master
   :target: https://coveralls.io/github/pyconll/pyconll?branch=master
.. |Documentation Status| image:: https://readthedocs.org/projects/pyconll/badge/?version=latest
   :target: https://pyconll.readthedocs.io/en/latest/?badge=latest
