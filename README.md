[![Build Status](https://travis-ci.org/pyconll/pyconll.svg?branch=master)](https://travis-ci.org/pyconll/pyconll)
[![Coverage Status](https://coveralls.io/repos/github/pyconll/pyconll/badge.svg?branch=master)](https://coveralls.io/github/pyconll/pyconll?branch=master)
[![Documentation Status](https://readthedocs.org/projects/pyconll/badge/?version=latest)](https://pyconll.readthedocs.io/en/latest/?badge=latest)

## pyconll

*Easily work with **CoNLL** files using the familiar syntax of **python**.*

The current version is 2.0. This version is fully functional, stable, tested, documented, and actively developed.

##### Links
- [Homepage](https://pyconll.github.io)
- [Documentation](https://pyconll.readthedocs.io/)


### Motivation

This tool is intended to be **minimal**, **low level**, and **functional** library in a widely used programming language.

There is a dissapointing lack of low level APIs for working with the  Universal Dependencies project. Current tooling focuses on graph transformations and DSLs for automated manipulation of CoNLL-U files. [Grew](http://grew.fr/) is a very powerful and productive tool, but there are limits to what its DSL can represent. [Treex](http://ufal.mff.cuni.cz/treex) is similar to Grew in this regard. On the other hand, [CL-CoNLLU](https://github.com/own-pt/cl-conllu/) is simple and low level, but its Common Lisp implementation reduces some of its functionality with other NLP projects. [UDAPI](http://udapi.github.io/)'s python API may fit the bill, but it is very large and difficult to get started with. So, ``pyconll`` creates a thin API on top of raw CoNLL annotations that is simple and intuitive in a popular language that can be used as building block in a complex system or the engine in small one off scripts.

Other useful tools can be found on the Universal Dependencies [website](https://universaldependencies.org/tools.html).

Hopefully, individual researchers will find use in this project, and will use it as a building block for more popular tools. By using ``pyconll``, researchers gain a standardized and feature rich base on which they can build larger projects and without worrying about CoNLL annotation and output.


### Code Snippet

```python
import pyconll

UD_ENGLISH_TRAIN = './ud/train.conll'

train = pyconll.load_from_file(UD_ENGLISH_TRAIN)

for sentence in train:
    for token in sentence:
        # Do work here.
        if token.form == 'Spain':
            token.upos = 'PROPN'
```

More examples can be found in the `examples` folder.


### Uses and Limitations

This package can edit CoNLL-U file annotations. Note that this does not include the actual text that is annotated. For this reason, word forms for Tokens are not editable and Sentence Tokens cannot be reassigned. Right now, this package allows for straight forward editing of annotation in the CoNLL-U format but does not include changing tokenization or creating completely new Sentences from scratch. If there is interest in this feature, please create a github issue for more visibility.


### Installation

As with most python packages, simply use `pip` to install from PyPi.

```
pip install pyconll
```

This package is designed for, and only tested with python 3.4 and will not be backported to python 2.x.


### Documentation

The full API documentation can be found online at [https://pyconll.readthedocs.io/](https://pyconll.readthedocs.io/). Examples can be found in the `examples` folder and also in the ``tests`` folder.


### Contributing

If you would like to contribute to this project you know the drill. Either create an issue and wait for me to repond and fix it or ignore it, or create a pull request or both. When cloning this repo, please run `make hooks` and `pip install -r requirements.txt` to properly setup the repo. `make hooks` setups up the pre-push hook, which ensures the code you push is formatted according to the default YAPF style. `pip install -r requirements.txt` simply sets up the environment with dependencies like `yapf`, `twine`, `sphinx`, and so on.


#### README and CHANGELOG

When changing either of these files, please change the Markdown version and run ``make docs`` so that the other versions stay in sync.


#### Code Formatting

Code formatting is done automatically on push if githooks are setup properly. The code formatter is [YAPF](https://github.com/google/yapf), and using this ensures that coding style stays consistent over time and between authors.
