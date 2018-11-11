# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

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
