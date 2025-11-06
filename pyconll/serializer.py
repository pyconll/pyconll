""" """

import io
from typing import Iterator

from pyconll.exception import FormatError
from pyconll.schema import TokenProtocol, compile_token_serializer
from pyconll.unit.sentence import Sentence


class Serializer[T: TokenProtocol]:
    """ """

    def __init__(self, schema: type[T], comment_marker: str = "#", delimiter: str = "\t") -> None:
        self.serializer = compile_token_serializer(schema)
        self.comment_marker = comment_marker
        self.delimiter = delimiter

    def serialize_token(self, token: T) -> str:
        return self.serializer(token, self.delimiter)

    def serialize_sentence(self, sentence: Sentence[T]) -> str:
        buffer = io.StringIO()
        self.write_sentence(sentence, buffer)
        return buffer.getvalue()

    def write_sentence(self, sentence: Sentence[T], writable: io.TextIOBase) -> None:
        for meta in sentence.meta.items():
            if meta[1] is not None:
                line = f"{self.comment_marker} {meta[0]} = {meta[1]}\n"
            else:
                line = f"{self.comment_marker} {meta[0]}\n"
            writable.write(line)

        for token in sentence.tokens:
            try:
                writable.write(self.serializer(token, self.delimiter))
                writable.write("\n")
            except FormatError as err:
                # TODO: Shouldn't this be any error??? Maybe if serialization is hidden on Token type
                raise FormatError(f"Error serializing sentence on token '{token!r}'.") from err

    def write_corpus(
        self, sentences: Iterator[Sentence[T]], writable: io.TextIOBase, separator: str = "\n"
    ) -> None:
        """ """
        for sentence in sentences:
            self.write_sentence(sentence, writable)
            writable.write(separator)
