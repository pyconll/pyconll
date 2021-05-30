CHANGELOG
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a
Changelog <http://keepachangelog.com/en/1.0.0/>`__ and this project
adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__.

[3.0.5] - 2021-05-29
--------------------

Fixed
~~~~~

-  Comments are output in the same order as they are read as.
   Previously, comments were sorted alphabetically before serialization.

.. _section-1:

[3.0.4] - 2021-02-24
--------------------

.. _fixed-1:

Fixed
~~~~~

-  The actual fix for the conda build to make sure the version is in
   lock-step across all uses, properly validated this time.

.. _section-2:

[3.0.3] - 2021-02-23
--------------------

.. _fixed-2:

Fixed
~~~~~

-  Fixed conda release temporarily by manually setting version number,
   this will be addressed in future deployment

.. _section-3:

[3.0.2] - 2021-02-23
--------------------

.. _fixed-3:

Fixed
~~~~~

-  Another attempt to fix the conda release pipeline

.. _section-4:

[3.0.1] - 2021-02-23
--------------------

.. _fixed-4:

Fixed
~~~~~

-  Fix issue with conda build where package name cannot be read from
   external sources anymore.

.. _section-5:

[3.0.0] - 2021-02-23
--------------------

.. _fixed-5:

Fixed
~~~~~

-  Handled multi-word tokens better in Tree creation by simply ignoring
   them since they do not interact with dependency relations.
-  Several linting and style issues on updating tools.
-  Conllable metaclass is now set properly in Python 3 method rather
   than old Python 2 method.
-  Several typos in the docstrings via new codespell linting process.
-  Thorough dependency cleanup and updating.

Changed
~~~~~~~

-  A Sentence with no root will throw a ValueError on Tree creation
   rather than returning an empty tree.
-  Continued changes and improvements with DevOps moving from TravisCI
   to GitHub actions, having better structured tests, typo checking as
   part of linting, etc.
-  Dependencies are now separated into build specific and other dev
   dependencies

Added
~~~~~

-  Type annotations the public and internal API
-  Added UD 2.7 to the list of versions validated against.
-  Revamped version mechanism so that this is now present within the
   actual module under ``pyconll.__version__`` as a string

Removed
~~~~~~~

-  Python 3.4 and 3.5 support was removed as part of supporting type
   annotations and staying up to date with the currently supported
   versions.
-  Loading or iterating from network url was removed. It introduced a
   dependency that was better removed, and did not seem to be used often
   in the wild. It also encourages inefficient design and can be easily
   replicated for those who need it.

.. _section-6:

[2.3.3] - 2020-10-25
--------------------

.. _fixed-6:

Fixed
~~~~~

-  Github action workflows were using old version of python that was no
   longer supported.

.. _section-7:

[2.3.2] - 2020-10-25
--------------------

.. _fixed-7:

Fixed
~~~~~

-  General quality improvements including documentation improvements,
   docstring improvements, better testing strategies, etc.
-  Clarified supported UD versions in README

.. _section-8:

[2.3.1] - 2020-10-06
--------------------

.. _fixed-8:

Fixed
~~~~~

-  PyPi workflow on release had improper repository url

.. _section-9:

[2.3] - 2020-10-06
------------------

.. _fixed-9:

Fixed
~~~~~

-  Bug in outputting enhanced dependencies when index had a range or was
   for an empty node
-  Typo in variable reference in documentation generation code
-  Corrected docstring for ``set_meta`` for the Sentence API

.. _added-1:

Added
~~~~~

-  ``remove_meta`` was added to the Sentence API thanks to alexeykosh

.. _changed-1:

Changed
~~~~~~~

-  Miscellaneous testing improvements and investments, Makefile
   improvements, release script improvements, and community improvements

.. _section-10:

[2.2.1] - 2019-11-17
--------------------

.. _fixed-10:

Fixed
~~~~~

-  Branding information typo within setup.py
-  Spurious command in Makefile recipe

.. _added-2:

Added
~~~~~

-  Added ``python_requires`` clause to setup.py to prevent installation
   on unsupported platforms
-  Include information in README about ``setuptools`` version needed to
   properly package within ``python_requires`` information
-  Conda packaging support along with information in README about new
   installation method

.. _changed-2:

Changed
~~~~~~~

-  ``pyconll`` version is now housed in .version file so that this
   version only needs to be changed in one place before release.

.. _section-11:

[2.2.0] - 2019-10-01
--------------------

.. _changed-3:

Changed
~~~~~~~

-  Use slots on Token and Sentence class for more efficient memory usage
   with large amounts of objects
-  Remove source fields on Token and Sentence. These were not an
   explicit part of the public API so this is not considered a breaking
   change.

.. _section-12:

[2.1.1] - 2019-09-04
--------------------

.. _fixed-11:

Fixed
~~~~~

-  Solved ``math.inf`` issue with python 3.4 where it does not exist

.. _section-13:

[2.1.0] - 2019-08-30
--------------------

.. _fixed-12:

Fixed
~~~~~

-  The example ``reannotate\_ngrams.py`` was out of sync with the
   function return type

.. _added-3:

Added
~~~~~

-  \`find_nonprojective_deps`\` was added to look for non-projective
   dependencies within a sentence

.. _section-14:

[2.0.0] - 2019-05-09
--------------------

.. _fixed-13:

Fixed
~~~~~

-  ``find_ngrams`` in the ``util`` module did not properly match case
   insensitivity.
-  ``conllable`` is now properly included in wildcard imports from
   ``pyconll``.
-  Issue when loading a CoNLL file over a network if the file contained
   UTF-8 characters. requests default assumes ASCII enconding on HTTP
   responses.
-  The Token columns deps and feats were not properly sorted by
   attribute (either numeric index or case invariant lexicographic sort)
   on serialization

.. _changed-4:

Changed
~~~~~~~

-  Clearer and more consise documentation
-  ``find_ngrams`` now returns the matched tokens as the last element of
   the yielded tuple.

.. _removed-1:

Removed
~~~~~~~

-  Document and paragraph ids on Sentences
-  Line numbers on Tokens and Sentences
-  Equality comparison on Tokens and Sentences. These types are mutable
   and implementing equality (with no hash overriding) causes issues for
   API clients.
-  ``SentenceTree`` module. This functionaliy was moved to the Sentence
   class method ``to_tree``.

.. _added-4:

Added
~~~~~

-  ``to_tree`` method on ``Sentence`` that returns the Tree representing
   the Sentence dependency structure

Security
~~~~~~~~

-  Updates to ``requirements.txt`` to patch Jinja2 and requests

.. _section-15:

[1.1.4] - 2019-04-15
--------------------

.. _fixed-14:

Fixed
~~~~~

-  Parsing of underscore’s for the form and lemma field, would
   automatically default to None, rather than the intended behavior.

.. _section-16:

[1.1.3] - 2019-01-03
--------------------

.. _fixed-15:

Fixed
~~~~~

-  When used on Windows, the default encoding of Windows-1252 was used
   when loading CoNLL-U files, however, CoNLL-U is UTF-8. This is now
   fixed.

.. _section-17:

[1.1.2] - 2018-12-28
--------------------

.. _added-5:

Added
~~~~~

-  *Getting Started* page on the documentation to make easier for
   newcomers

.. _fixed-16:

Fixed
~~~~~

-  Versioning on docs page which had not been properly updated
-  Some documentation errors
-  ``requests`` version used in ``requirements.txt`` was insecure and
   updated to newer version

.. _section-18:

[1.1.1] - 2018-12-10
--------------------

.. _fixed-17:

Fixed
~~~~~

-  The ``pyconll.tree`` module was not properly included before in
   ``setup.py``

.. _section-19:

[1.1.0] - 2018-11-11
--------------------

.. _added-6:

Added
~~~~~

-  ``pylint`` to build process
-  ``Conllable`` abstract base class to mark CoNLL serializable
   components
-  Tree data type construction of a sentence

.. _changed-5:

Changed
~~~~~~~

-  Linting patches suggested by ``pylint``.
-  Removed ``_end_line_number`` from ``Sentence`` constructor. This is
   an internal patch, as this parameter was not meant to be used by
   callers.
-  New, improved, and clearer documentation
-  Update of ``requests`` dependency due to security flaw

.. _section-20:

[1.0.1] - 2018-09-14
--------------------

.. _changed-6:

Changed
~~~~~~~

-  Removed test packages from final shipped package.

.. _section-21:

[1.0] - 2018-09-13
------------------

.. _added-7:

Added
~~~~~

-  There is now a FormatError to help make debugging easier if the
   internal data of a Token is put into an invalid state. This error
   will be seen on running ``Token#conll``.
-  Certain token fields with empty values, were not output when calling
   ``Token#conll`` and were instead ignored. This situation now causes a
   FormatError.
-  Stricter parsing and validation of general CoNLL guidelines.

.. _fixed-18:

Fixed
~~~~~

-  ``DEPS`` parsing was broken before and assumed that there was less
   information than is actually possible in the UD format. This means
   that now ``deps`` is a tuple with cardinality 4.

.. _section-22:

[0.3.1] - 2018-08-08
--------------------

.. _fixed-19:

Fixed
~~~~~

-  Fixed issue with submodules not being packaged in build

.. _section-23:

[0.3] - 2018-07-28
------------------

.. _added-8:

Added
~~~~~

-  Ability to easily load CoNLL files from a network path (url)
-  Some parsing validation. Before the error was not caught up front so
   the error could unexpectedly later show up.
-  Sentence slicing had an issue before if either the start or end was
   omittted.
-  More documentation and examples.
-  Conll is now a ``MutableSequence``, so it handles methods beyond its
   implementation as well as defined by python.

.. _fixed-20:

Fixed
~~~~~

-  Some small bug fixes with parsing the token dicts.

.. _section-24:

[0.2.3] - 2018-07-23
--------------------

.. _fixed-21:

Fixed
~~~~~

-  Issues with documentation since docstrings were not in RST. Fixed by
   using napoleon sphinx extension

.. _added-9:

Added
~~~~~

-  A little more docs
-  More README info
-  Better examples

.. _section-25:

[0.2.2] - 2018-07-18
--------------------

.. _fixed-22:

Fixed
~~~~~

-  Installation issues again with wheel when using ``pip``.

.. _section-26:

[0.2.1] - 2018-07-18
--------------------

.. _fixed-23:

Fixed
~~~~~

-  Installation issues when using ``pip``

.. _section-27:

[0.2] - 2018-07-16
------------------

.. _added-10:

Added
~~~~~

-  More documentation
-  Util package for convenient and common logic

.. _section-28:

[0.1.1] - 2018-07-15
--------------------

.. _added-11:

Added
~~~~~

-  Documentation which can be found
   `here <https://pyconll.readthedocs.io/en/latest/>`__.
-  Small documentation changes on methods.

.. _section-29:

[0.1] - 2018-07-04
------------------

.. _added-12:

Added
~~~~~

-  Everything. This is the first release of this package. The most
   notable absence is documentation which will be coming in a
   near-future release.
