"""
"""

from typing import Any, Iterator

from pyconll.exception import FormatError
from pyconll.schema import TokenProtocol
from pyconll.unit.sentence import Sentence


class Writer:
    """ """

    def __init__(self, comment_marker: str = "#", delimiter: str = "\t") -> None:
        self.comment_marker = comment_marker
        self.delimiter = delimiter

    def write[T: TokenProtocol](self, sentences: Iterator[Sentence[T]], writable: Any) -> None:
        for sentence in sentences:
            for meta in sentence.meta.items():
                if meta[1] is not None:
                    line = f"{self.comment_marker} {meta[0]} = {meta[1]}"
                else:
                    line = f"{self.comment_marker} {meta[0]}"
                writable.write(line)
                writable.write("\n")

            for token in sentence.tokens:
                try:
                    writable.write(token.conll())
                    writable.write("\n")
                except FormatError as err:
                    # TODO: Shouldn't this be any error??? Maybe if serialization is hidden on Token type
                    raise FormatError(f"Error serializing sentence on token '{token!r}'.") from err

            writable.write("\n")