### Contributing Guidelines

Contributing to pyconll should be relatively straightfoward. The following are a set of guidelines for contribution and should be used when submitting PRs for pyconll.

* All PRs should be opened against the `dev` branch. `dev` is merged into `master` to release the next version. This separates released code from "staged" changes. So changes will have to wait until the next release for their code to flow to master.
* Any new methods, classes, or modules should have corresponding docstrings at each level. These docstrings are used to automatically generate documentation for `readthedocs.org`, so high-quality, informative comments are critical. These formats should follow the [Google docstring](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) as shown for the napoleon sphynx extension. The full Google style can be found [here](http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
* Any new code must at least be covered by an existing test case, and preferebly should add or change appropriate test cases depending on the size of the change. This will be validated by coveralls to make sure code coverage remains high.
* Setup githooks to keep code quality. This can be done via running `make hooks`. On push, this will make sure that code follows the defined guidelines by [yapf](https://github.com/google/yapf).
