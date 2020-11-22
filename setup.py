import os
import re
from setuptools import setup


def read(fn):
    """
    Read the contents of the provided filename.

    The filename is relative to the contents of the current file location.

    Args:
    fn: The filename to read in.

    Returns:
    The contents of the file.
    """
    abs_fn = os.path.join(os.path.dirname(__file__), fn)
    f = open(abs_fn)
    contents = f.read()
    f.close()

    return contents


def parse_version(fn):
    """
    Parse the version from specified file, assumed to be a versioner module.

    The filename is relative to the contents of the current file location.

    Args:
        fn: The filename to read in.

    Returns:
        The parsed version file.

    Raises:
        ValueError: If the file is deemed not clear enough to determine version
            information.
    """
    contents = read(fn)

    # Note that this regex version check is very simple and is not all encompassing
    # but works fine for the given use case and internal nature of the logic.
    m = re.search('__version__\\s*=\\s*[\'"]((\\d+\\.)+(\\d+))[\'"]', contents)

    if not m:
        raise ValueError(
            'There is no version string identified in the file contents.')

    ver = m.group(1)
    return ver


setup(
    name = 'pyconll',
    packages = ['pyconll', 'pyconll.unit', 'pyconll.tree'],
    version = parse_version('pyconll/_version.py'),
    description = 'Read and manipulate CoNLL files',
    long_description = read('README.rst'),
    author = 'Matias Grioni',
    author_email = 'matgrioni@gmail.com',
    url = 'https://github.com/pyconll/pyconll',
    license = 'MIT',
    keywords = ['nlp', 'conllu', 'conll', 'universal dependencies'],
    python_requires = '~=3.4',
    install_requires = [
        'requests >= 2.21'
    ],
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
