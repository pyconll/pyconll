[![CI](https://github.com/pyconll/pyconll/actions/workflows/ci.yml/badge.svg)](https://github.com/pyconll/pyconll/actions/workflows/ci.yml)
[![DI](https://github.com/pyconll/pyconll/actions/workflows/di.yml/badge.svg)](https://github.com/pyconll/pyconll/actions/workflows/di.yml)
[![Coverage Status](https://coveralls.io/repos/github/pyconll/pyconll/badge.svg?branch=master)](https://coveralls.io/github/pyconll/pyconll?branch=master)
[![Documentation Status](https://readthedocs.org/projects/pyconll/badge/?version=stable)](https://pyconll.readthedocs.io/en/stable)
[![Version](https://img.shields.io/github/v/release/pyconll/pyconll)](https://github.com/pyconll/pyconll/releases)
[![gitter](https://badges.gitter.im/pyconll/pyconll.svg)](https://gitter.im/pyconll/pyconll?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## pyconll

*Easily work with **CoNLL** files using the familiar syntax of **python**.*

<img src="https://raw.githubusercontent.com/pyconll/pyconll/refs/heads/master/res/logo.svg" width="256px" height="256px">

##### Links
- [Homepage](https://pyconll.github.io)
- [Documentation](https://pyconll.readthedocs.io/)


### Installation

As with most python packages, simply use `pip` to install from PyPi.

```
pip install pyconll
```

`pyconll` is also *usually* available as a conda package on the `pyconll` channel. Packages in the version range [2.2.0, 4.0.0a0) are on conda. Version 4.0.0 will be added once conda adds full support for python 3.14

```
conda install -c pyconll pyconll
```

The 4.0 release of pyconll only supports Python 3.14 and newer. Earlier releases cover other LTS Python versions but 4.0 introduced a large revamp to pyconll which significantly improved parsing flexibility and efficiency, while also improving the object model to better align with actual usage. It is recommended to move to this version if possible, and only bug patches will be taken on pre-4.0.0 versions.


### Use

This tool is intended to be a **minimal**, **low level**, **expressive** and **pragmatic** library in a widely used programming language. pyconll creates a thin API on top of raw CoNLL annotations that is simple and intuitive.

It offers the following features:
* Regular CI testing and validation against all UD v2.x versions to ensure compatibility.
* A flexible schema system for working with CoNLL-U (and now custom tabular formats).
* A typed API for better development experience and better semantics.
* A focus on usability and simplicity in design (zero runtime dependencies)
* Various performance optimizations for smaller memory footprint and faster parsing.

See the following code example to understand the basics of the API.

```python
# This snippet finds sentences where a token marked with part of speech 'AUX' are
# governed by a NOUN. For example, in French this is a less common construction
# and we may want to validate these examples because we have previously found some
# problematic examples of this construction.
from pyconll.conllu import conllu

train = conllu.load_from_file('./ud/train.conllu')

review_sentences = []

# The loaded data is a list of Sentences, and sentences contain tokens.
# Sentences also de/serialize comment information.
for sentence in train:
    # Build a token index for lookups
    token_by_id = {t.id: t for t in sentence.tokens}

    for token in sentence.tokens:
        # Tokens have attributes such as upos, head, id, deprel, etc.
        # We must check that the token is not the root token.
        if token.upos == 'AUX' and token.head != '0':
            head_token = token_by_id.get(token.head)
            if head_token and head_token.upos == 'NOUN':
                review_sentences.append(sentence)
                break

print('Review the following sentences:')
for sent in review_sentences:
    print(sent.meta['sent_id'])
```

A full definition of the API can be found in the [documentation](https://pyconll.readthedocs.io/) or follow the [quick start guide](https://pyconll.readthedocs.io/en/stable/starting.html) for a focused introduction.


### Migrating to Version 4.0

Version 4.0 introduces significant architectural improvements that require some code changes. Here's how to migrate from earlier versions to 4.0:

#### Import Changes

**Before:**
```python
import pyconll

corpus = pyconll.load_from_file('train.conllu')
```

**After:**
```python
from pyconll.conllu import conllu

corpus = conllu.load_from_file('train.conllu')
```

#### Return Type Changes

The `load_from_file` and similar methods now return `list[Sentence[Token]]` instead of a `Conll` object. The only real purpose of `Conll` was to be sentence container and be able to serialize the entire corpus.

**Before:**
```python
corpus = pyconll.load_from_file('train.conllu')  # Returns Conll object
for sentence in corpus:  # Conll is MutableSequence
    pass
```

**After:**
```python
corpus = conllu.load_from_file('train.conllu')  # Returns list[Sentence]
for sentence in corpus:  # Standard Python list
    pass
```

#### Sentence Changes

Sentences no longer support indexing tokens by ID. The motivation behind this is that it was creating an extra data structure when it may not be needed for the application, and also Sentences for the moment are generic to the Token type, and this relationship may not exist in other Token types. Build your own index if needed, but a future version may introduce an appropriate generic Sentence construction to automatically build this structure at parse time:

**Before:**
```python
for sentence in corpus:
    for token in sentence:
        if token.head != '0':
            head_token = sentence[token.head]  # Direct ID lookup
```

**After:**
```python
for sentence in corpus:
    token_by_id = {t.id: t for t in sentence.tokens}
    for token in sentence.tokens:
        if token.head != '0':
            head_token = token_by_id[token.head]
```

Metadata access also changed. There are no longer special metadata fields (since Sentence is generic to Token type). The general principles of singleton keys and whitespace trimming remain the same.

**Before:**
```python
sentence_id = sentence.id
sentence_text = sentence.text
```

**After:**
```python
sentence_id = sentence.meta['sent_id']
sentence_text = sentence.meta['text']
```

#### Tree Changes

Tree creation is now a separate function rather than a method on Sentence:

**Before:**
```python
tree = sentence.to_tree()
```

**After:**
```python
from pyconll.conllu import tree_from_tokens

tree = tree_from_tokens(sentence.tokens)
```

#### Serialization Changes

Serialization no longer uses `.conll()` methods. Use `WriteFormat` methods instead:

**Before:**
```python
# Serialize to string
conll_string = corpus.conll()

# Write to file
with open('output.conllu', 'w') as f:
    corpus.write(f)
```

**After:**
```python
# Serialize individual items
from pyconll.conllu import conllu

# Write to file
with open('output.conllu', 'w') as f:
    conllu.write_corpus(corpus, f)
```

### Custom Formats (New in 4.0)

Version 4.0 introduced a flexible schema system (`TokenSchema`) that allows you to define custom token formats beyond CoNLL-U. This makes it possible to work with CoNLL-X, CoNLL 2006, or any other column-based format by defining your own token schema and creating a `Format` instance. Since I do not currently have much experience with these other formats I have not pre-added them to this library, but my expectation is that in time, these definitions will be filled out.

```python
from typing import Optional
from pyconll.format import Format
from pyconll.schema import TokenSchema, field, nullable, unique_array
from pyconll.shared import Sentence

class MyToken(TokenSchema):
    id: int
    form: Optional[str] = field(nullable(str, "_"))
    lemma: Optional[str] = field(nullable(str, "_"))
    pos: str
    head: int
    deprel: str
    feats: set[str] = field(unique_array(str, ",", "_"))
my_format = Format(MyToken, Sentence[MyToken], delimiter='\t')

token_line = "3\ttest\t_\tNOUN\t2\tAUX\tfeat1,feat2"
first_token: MyToken = my_format.parse_token(token_line)
assert ((first_token.id, first_token.form, first_token.lemma, first_token.feats) == (3, 'test', None, {"feat1", "feat2"}))

empty_feats_token_line = "4\tanother\t_\tNOUN\t2\tAUX\t_"
second_token: MyToken = my_format.parse_token(empty_feats_token_line)
assert ((first_token.id, first_token.form, first_token.lemma, first_token.feats) == (4, 'another', None, {}))

sentences = my_format.load_from_file('data.conll')
```

For more details, see the [documentation](https://pyconll.readthedocs.io/) or samples in the examples folder.


### Contributing

Contributions to this project are welcome and encouraged! If you are unsure how to contribute, here is a [guide](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork) from Github explaining the basic workflow. After cloning this repo, please run `pip install -r requirements.txt` to properly setup locally.

#### Release Checklist

Below enumerates the general release process explicitly. This section is for internal use and most people do not have to worry about this. First note, that the dev branch is always a direct extension of master with the latest changes since the last release. That is, it is essentially a staging release branch.

* Change the version in `pyconll/_version` appropriately.
* Merge dev into master **locally**. Github does not offer a fast forward merge and explicitly uses --no-ff. So to keep the linear nature of changes, merge locally to fast forward. This is assuming that the dev branch looks good on CI tests which do not automatically run in this situation.
* Push the master branch. This should start some CI tests specifically for master. After validating these results, create a tag corresponding to the next version number and push the tag.
* Create a new release from this tag from the [Releases page](https://github.com/pyconll/pyconll/releases). On creating this release, two workflows will start. One releases to pypi, and the other releases to conda.
* Validate these workflows pass, and the package is properly released on both platforms.
