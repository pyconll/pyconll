|Build Status| |Coverage Status| |Documentation Status|

pyconll
-------

A simple package with simple intentions. Easily manipulate conll files
using the familiar syntax of python. The current version is 0.1. This is
a pretty stable version, passes a lot of tests and has full
functionality essentially. The only thing that is missing is
documentation which will be coming soon.

Motivation
~~~~~~~~~~

When working with the Universal Dependencies project, I was dissapointed
with the lack of good API options for maniuplating the conll files.
There are plenty of good tools, but none of which are general purpose
enough. Grew is a great tool, that I found was slightly limiting for
some tasks (and extremely productive for others). Treex is similar to
grew in this regard. CL-CoNLLU is essentailly what I needed, but it is
written in a language that many are not familiar with, Lisp. UDAPI might
fit the bill with its python API, but the package itself is quite large
and the documentation impossible to get through. Other tools can be
found on the Universal Dependencies page and all are very nice pieces of
software. But I found that all of them were lacking for my usage
pattern. I was looking for a thin API on top of raw CoNLL-U annotations
that was simple and intuitive. This is my attempt at a small, minimal,
and intuitive package in a popular language that can be used as one step
a in complex systems or small one off scripts.

I hope that individual researchers will find use in this project, and
that they can use it as a building block for more popular tools. By
using ``pyconll``, researchers gain a standardized and feature rich base
on which they can build larger projects and not worry about CoNLL
annotation and output.

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

Install
~~~~~~~

Installation is easy like with most python packages. Simply use ``pip``
to install from PyPi.

::

    pip install pyconll

This package is designed for, and only tested with python 3.4 and above.
Backporting to python 2.7 is not in future plans.

Documentation
~~~~~~~~~~~~~

Documentation is essential to learning how to use any library. The full
API documentation can be found online at
https://pyconll.readthedocs.io/en/latest/. Examples are also important
and I've created a few examples to see usage of this library in the
``examples`` folder. These examples can also be found on the online
documentation.

Contributing
~~~~~~~~~~~~

If you would like to contribute to this project you know the drill.
Either create an issue and wait for me to repond and fix it or ignore
it, or create a PR (pull request) or both. When cloning this repo,
please run ``make hooks`` and ``pip install -r requirements.txt`` to
properly setup the repo. ``make hooks`` setups up the pre-push hook,
which ensures the code you push is formatted according to the default
YAPF style. ``pip install -r requirements.txt`` simply sets up the
environment with dependencies like ``yapf``, ``twine``, ``sphinx``, and
so on.

.. |Build Status| image:: https://travis-ci.org/matgrioni/pyconll.svg?branch=master
   :target: https://travis-ci.org/matgrioni/pyconll
.. |Coverage Status| image:: https://coveralls.io/repos/github/matgrioni/pyconll/badge.svg?branch=master
   :target: https://coveralls.io/github/matgrioni/pyconll?branch=master
.. |Documentation Status| image:: https://readthedocs.org/projects/pyconll/badge/?version=latest
   :target: https://pyconll.readthedocs.io/en/latest/?badge=latest
