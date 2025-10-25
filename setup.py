from pathlib import Path
from setuptools import setup

from util import parse


def make_relative(fn):
    """
    Make the filename relative to the current file.

    Args:
        fn: The filename to convert.

    Returns:
        The path relative to the current file.
    """
    return Path(__file__).parent / fn


setup(
    name = 'pyconll',
    packages = ['pyconll', 'pyconll.unit', 'pyconll.tree'],
    version = parse.package_version(make_relative('pyconll/_version.py')),
    description = 'Read and manipulate CoNLL files',
    long_description = make_relative('README.md').read_text(),
    long_description_content_type="text/markdown",
    author = 'Matias Grioni',
    author_email = 'matgrioni@gmail.com',
    url = 'https://github.com/pyconll/pyconll',
    license = 'MIT',
    keywords = ['nlp', 'conllu', 'conll', 'universal dependencies'],
    python_requires = '~=3.14',
    package_data = { 'pyconll': ['py.typed'] },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities'
    ]
)
