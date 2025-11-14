"""
A library whose purpose is to provide a low level layer between the CoNLL format
and python code.
"""

import pathlib

__all__ = ["conllu", "exception", "format", "schema", "sentence", "tree"]
__version__ = (pathlib.Path(__file__).parent / "_version").read_text().strip()
