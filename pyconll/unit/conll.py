"""
Defines the Conll type and the associated parsing and output logic.
"""

from typing import Any

from pyconll.conllable import Conllable
from pyconll.schema import TokenProtocol
from pyconll.unit.sentence import Sentence


class Conll[T: TokenProtocol](Conllable):
    """
    The abstraction for a CoNLL-U file. A CoNLL-U file is more or less just a
    collection of sentences in order. These sentences are accessed by numeric
    index. Note that sentences must be separated by whitespace. CoNLL-U also
    specifies that the file must end in a new line but that requirement is
    relaxed here in parsing.
    """

    def __init__(self, sentences: list[Sentence[T]]) -> None:
        """
        Create a CoNLL-U file collection of sentences.

        Args:
            sentences: The sentences to put into this Conll object.
        """
        self._sentences: list[Sentence[T]] = sentences

    def conll(self) -> str:
        """
        Output the Conll object to a CoNLL-U formatted string.

        Returns:
            The CoNLL-U object as a string. This string will end in a newline.

        Raises:
            FormatError: If there are issues converting the sentences to the
                CoNLL format.
        """
        # Add newlines along with sentence strings so that there is no need to
        # slice potentially long lists or modify strings.
        components = list(map(lambda sent: sent.conll(), self._sentences))
        components.append("")

        return "\n\n".join(components)

    def write(self, writable: Any) -> None:
        """
        Write the Conll object to something that is writable.

        For file writing, this method is more efficient than calling conll then
        writing since no string of the entire Conll object is created. The output
        includes a final newline as detailed in the CoNLL-U specification.

        Args:
            writable: The writable object such as a file. Must have a write
                method.
        """
        for sentence in self._sentences:
            writable.write(sentence.conll())
            writable.write("\n\n")
