from distutils.core import setup

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
    name = 'pyconllu',
    packages = ['pyconllu'],
    version = '0.1',
    description = 'Read and maniuplate CoNLL-U files',
    long_description = read('README.rst'),
    author = 'Matias Grioni',
    author_email = 'matgrioni@gmail.com',
    url = 'https://github.com/matgrioni/pyconllu',
    license = 'MIT',
    keywords = ['nlp', 'conllu', 'conll', 'universal dependencies'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intented Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities'
    ]
)
