|Build Status| |Coverage Status|

pyconll
-------

A simple package with simple intentions. Easily manipulate conll files
using the familiar syntax of python. The current version is 0.1. This is
a pretty stable version, passes a lot of tests and has full
functionality essentially. The only thing that is missing is
documentation which will be coming soon.

Motivation
----------

When working with the Universal Dependencies project, I was dissapointed
with the lack of good API options for maniuplating the conll files.
There are plenty of good tools, none of which are general purpose
enough. Grew is a great tool, but I found was slightly limiting for some
tasks (and extremely productive for others). Treex is similar to grew in
this regard. CL-CoNLLU is essentailly what I need, but it written in a
language that many are not familiar with, Lisp. UDAPI might fit the
bill, but it takes a while to go through the documentation and the
package itself is quite large. More tools can be found on the Universal
Dependencies page, but I found that all of them were lacking for my
usage pattern. Namely, conll file manipulation in python in a simple,
and intuitive way. This is my attempt at a small, intuitive package in a
popular language that can be used in complex systems or small one off
scripts.

Uses
----

The usage of this package is to enable editing of CoNLL-U format
annotations of sentences. For this reason, word forms for Tokens are not
editable and Sentence Tokens cannot be reassigned. Right now, this
package seeks to allow for straight forward editing of annotation in the
CoNLL-U format. This does not include changing tokenization or creating
completely new Sentences from scratch.

Install
-------

Installation is easy like with most python packages. Simply use ``pip``
to install from PyPi.

::

    pip install pyconll

This package is designed for, and only tested with python 3.4 and above.

.. |Build Status| image:: https://travis-ci.org/matgrioni/pyconll.svg?branch=master
   :target: https://travis-ci.org/matgrioni/pyconll
.. |Coverage Status| image:: https://coveralls.io/repos/github/matgrioni/pyconll/badge.svg?branch=master
   :target: https://coveralls.io/github/matgrioni/pyconll?branch=master
