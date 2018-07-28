from setuptools import setup
import os

def read(fn):
    """
    Read the contents of the provided filename.

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

setup(
    name = 'pyconll',
    packages = ['pyconll'],
    version = '0.3',
    description = 'Read and maniuplate CoNLL files',
    long_description = read('README.rst'),
    author = 'Matias Grioni',
    author_email = 'matgrioni@gmail.com',
    url = 'https://github.com/pyconll/pyconll',
    license = 'MIT',
    keywords = ['nlp', 'conllu', 'conll', 'universal dependencies'],
    install_requires =[
        'requests >= 2.19'
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
