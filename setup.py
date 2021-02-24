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
    long_description = make_relative('README.rst').read_text(),
    author = 'Matias Grioni',
    author_email = 'matgrioni@gmail.com',
    url = 'https://github.com/pyconll/pyconll',
    license = 'MIT',
    keywords = ['nlp', 'conllu', 'conll', 'universal dependencies'],
    python_requires = '~=3.6',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities'
    ]
)
