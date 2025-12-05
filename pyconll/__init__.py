"""
A library whose purpose is to provide a low level layer between the CoNLL format
and python code.
"""

import pathlib

__all__ = ["conllu", "exception", "format", "schema", "tree"]
__version__ = (pathlib.Path(__file__).parent / "_version").read_text().strip()

# It's odd but it removes pathlib from the pyconll module.
del pathlib
