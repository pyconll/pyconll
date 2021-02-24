# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [3.0.3] - 2021-02-23
### Fixed
- Fixed conda release temporarily by manually setting version number, this will be addressed in future deployment

## [3.0.2] - 2021-02-23
### Fixed
- Another attempt to fix the conda release pipeline

## [3.0.1] - 2021-02-23
### Fixed
- Fix issue with conda build where package name cannot be read from external sources anymore.

## [3.0.0] - 2021-02-23
### Fixed
- Handled multi-word tokens better in Tree creation by simply ignoring them since they do not interact with dependency relations.
- Several linting and style issues on updating tools.
- Conllable metaclass is now set properly in Python 3 method rather than old Python 2 method.
- Several typos in the docstrings via new codespell linting process.
- Thorough dependency cleanup and updating.

### Changed
- A Sentence with no root will throw a ValueError on Tree creation rather than returning an empty tree.
- Continued changes and improvements with DevOps moving from TravisCI to GitHub actions, having better structured tests, typo checking as part of linting, etc.
- Dependencies are now separated into build specific and other dev dependencies

### Added
- Type annotations the public and internal API
- Added UD 2.7 to the list of versions validated against.
- Revamped version mechanism so that this is now present within the actual module under `pyconll.__version__` as a string

### Removed
- Python 3.4 and 3.5 support was removed as part of supporting type annotations and staying up to date with the currently supported versions.
- Loading or iterating from network url was removed. It introduced a dependency that was better removed, and did not seem to be used often in the wild. It also encourages inefficient design and can be easily replicated for those who need it.

## [2.3.3] - 2020-10-25
### Fixed
- Github action workflows were using old version of python that was no longer supported.

## [2.3.2] - 2020-10-25
### Fixed
- General quality improvements including documentation improvements, docstring improvements, better testing strategies, etc.
- Clarified supported UD versions in README

## [2.3.1] - 2020-10-06
### Fixed
- PyPi workflow on release had improper repository url

## [2.3] - 2020-10-06
### Fixed
- Bug in outputting enhanced dependencies when index had a range or was for an empty node
- Typo in variable reference in documentation generation code
- Corrected docstring for `set_meta` for the Sentence API

### Added
- `remove_meta` was added to the Sentence API thanks to alexeykosh

### Changed
- Miscellaneous testing improvements and investments, Makefile improvements, release script improvements, and community improvements

## [2.2.1] - 2019-11-17
### Fixed
- Branding information typo within setup.py 
- Spurious command in Makefile recipe

### Added
- Added `python_requires` clause to setup.py to prevent installation on unsupported platforms
- Include information in README about `setuptools` version needed to properly package within `python_requires` information
- Conda packaging support along with information in README about new installation method

### Changed
- `pyconll` version is now housed in .version file so that this version only needs to be changed in one place before release.

## [2.2.0] - 2019-10-01
### Changed
- Use slots on Token and Sentence class for more efficient memory usage with large amounts of objects
- Remove source fields on Token and Sentence. These were not an explicit part of the public API so this is not considered a breaking change.

## [2.1.1] - 2019-09-04
### Fixed
- Solved ``math.inf`` issue with python 3.4 where it does not exist

## [2.1.0] - 2019-08-30
### Fixed
- The example ``reannotate\_ngrams.py`` was out of sync with the function return type

### Added
- `find_nonprojective_deps`` was added to look for non-projective dependencies within a sentence

## [2.0.0] - 2019-05-09
### Fixed
- ``find_ngrams`` in the ``util`` module did not properly match case insensitivity.
- ``conllable`` is now properly included in wildcard imports from ``pyconll``.
- Issue when loading a CoNLL file over a network if the file contained UTF-8 characters. requests default assumes ASCII enconding on HTTP responses.
- The Token columns deps and feats were not properly sorted by attribute (either numeric index or case invariant lexicographic sort) on serialization

### Changed
- Clearer and more consise documentation
- ``find_ngrams`` now returns the matched tokens as the last element of the yielded tuple.

### Removed
- Document and paragraph ids on Sentences
- Line numbers on Tokens and Sentences
- Equality comparison on Tokens and Sentences. These types are mutable and implementing equality (with no hash overriding) causes issues for API clients.
- ``SentenceTree`` module. This functionaliy was moved to the Sentence class method ``to_tree``.

### Added
- ``to_tree`` method on ``Sentence`` that returns the Tree representing the Sentence dependency structure

### Security
- Updates to ``requirements.txt`` to patch Jinja2 and requests

## [1.1.4] - 2019-04-15
### Fixed
- Parsing of underscore's for the form and lemma field, would automatically default to None, rather than the intended behavior.

## [1.1.3] - 2019-01-03
### Fixed
- When used on Windows, the default encoding of Windows-1252 was used when loading CoNLL-U files, however, CoNLL-U is UTF-8. This is now fixed.

## [1.1.2] - 2018-12-28
### Added
- *Getting Started* page on the documentation to make easier for newcomers

### Fixed
- Versioning on docs page which had not been properly updated
- Some documentation errors
- ``requests`` version used in ``requirements.txt`` was insecure and updated to newer version

## [1.1.1] - 2018-12-10
### Fixed
- The ``pyconll.tree`` module was not properly included before in ``setup.py``

## [1.1.0] - 2018-11-11
### Added
- ``pylint`` to build process
- ``Conllable`` abstract base class to mark CoNLL serializable components
- Tree data type construction of a sentence

### Changed
- Linting patches suggested by ``pylint``.
- Removed ``_end_line_number`` from ``Sentence`` constructor. This is an internal patch, as this parameter was not meant to be used by callers.
- New, improved, and clearer documentation
- Update of ``requests`` dependency due to security flaw

## [1.0.1] - 2018-09-14
### Changed
- Removed test packages from final shipped package.

## [1.0] - 2018-09-13
### Added
- There is now a FormatError to help make debugging easier if the internal data of a Token is put into an invalid state. This error will be seen on running `Token#conll`.
- Certain token fields with empty values, were not output when calling `Token#conll` and were instead ignored. This situation now causes a FormatError.
- Stricter parsing and validation of general CoNLL guidelines.

### Fixed
- `DEPS` parsing was broken before and assumed that there was less information than is actually possible in the UD format. This means that now `deps` is a tuple with cardinality 4.

## [0.3.1] - 2018-08-08
### Fixed
- Fixed issue with submodules not being packaged in build

## [0.3] - 2018-07-28
### Added
- Ability to easily load CoNLL files from a network path (url)
- Some parsing validation. Before the error was not caught up front so the error could unexpectedly later show up.
- Sentence slicing had an issue before if either the start or end was omittted.
- More documentation and examples.
- Conll is now a ``MutableSequence``, so it handles methods beyond its implementation as well as defined by python.

### Fixed
- Some small bug fixes with parsing the token dicts.

## [0.2.3] - 2018-07-23
### Fixed
- Issues with documentation since docstrings were not in RST. Fixed by using napoleon sphinx extension

### Added
- A little more docs
- More README info
- Better examples

## [0.2.2] - 2018-07-18
### Fixed
- Installation issues again with wheel when using ``pip``.

## [0.2.1] - 2018-07-18
### Fixed
- Installation issues when using ``pip``

## [0.2] - 2018-07-16
### Added
- More documentation
- Util package for convenient and common logic

## [0.1.1] - 2018-07-15
### Added
- Documentation which can be found [here](https://pyconll.readthedocs.io/en/latest/).
- Small documentation changes on methods.

## [0.1] - 2018-07-04
### Added
- Everything. This is the first release of this package. The most notable absence is documentation which will be coming in a near-future release.
