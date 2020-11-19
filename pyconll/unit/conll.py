"""
Defines the Conll type and the associated parsing and output logic.
"""

from typing import Any, Iterable, Iterator, List, Union, MutableSequence, overload

import pyconll._parser
from pyconll.conllable import Conllable
from pyconll.unit.sentence import Sentence


class Conll(MutableSequence[Sentence], Conllable):
    """
    The abstraction for a CoNLL-U file. A CoNLL-U file is more or less just a
    collection of sentences in order. These sentences are accessed by numeric
    index. Note that sentences must be separated by whitespace. CoNLL-U also
    specifies that the file must end in a new line but that requirement is
    relaxed here in parsing.
    """
    def __init__(self, it: Iterable[str]) -> None:
        """
        Create a CoNLL-U file collection of sentences.

        Args:
            it: An iterator of the lines of the CoNLL-U file.

        Raises:
            ParseError: If there is an error constructing the sentences in the
                iterator.
        """
        self._sentences: List[Sentence] = []

        for sentence in pyconll._parser.iter_sentences(it):
            self._sentences.append(sentence)

    def conll(self) -> str:
        """
        Output the Conll object to a CoNLL-U formatted string.

        Returns:
            The CoNLL-U object as a string. This string will end in a newline.
        """
        # Add newlines along with sentence strings so that there is no need to
        # slice potentially long lists or modify strings.
        components = list(map(lambda sent: sent.conll(), self._sentences))
        components.append('')

        return '\n\n'.join(components)

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
            writable.write('\n\n')

    def insert(self, index: int, value: Sentence) -> None:
        """
        Insert the given sentence into the given location.

        This function behaves in the same way as python lists insert.

        Args:
            index: The numeric index to insert the sentence into.
            value: The sentence to insert.
        """
        self._sentences.insert(index, value)

    def __contains__(self, other: object) -> bool:
        """
        Check if the Conll object has this sentence.

        Args:
            other: The sentence to check for.

        Returns:
            True if this Sentence is exactly in the Conll object. False,
            otherwise.
        """
        return other in self._sentences

    def __iter__(self) -> Iterator[Sentence]:
        """
        Allows for iteration over every sentence in the CoNLL-U file.

        Yields:
            An iterator over the sentences in this Conll object.
        """
        for sentence in self._sentences:
            yield sentence

    @overload
    def __getitem__(self, key: int) -> Sentence:
        pass

    @overload
    def __getitem__(self, key: slice) -> 'Conll':
        pass

    def __getitem__(self, key):
        """
        Index a sentence by key value.

        Args:
            key: The key to index the sentence by. This key can either be a
                numeric key, or a slice.

        Returns:
            The corresponding sentence if the key is an int or the sentences
            if the key is a slice in the form of another Conll object.

        Raises:
            TypeError: If the key is not an integer or slice.
        """
        if isinstance(key, int):
            return self._sentences[key]

        if isinstance(key, slice):
            sliced_conll = Conll([])
            sliced_conll._sentences = self._sentences[key]

            return sliced_conll

        raise TypeError('Conll indices must be ints or slices.')

    @overload
    def __setitem__(self, key: int, sent: Sentence) -> None:
        pass

    @overload
    def __setitem__(self, key: slice, sents: Iterable[Sentence]) -> None:
        pass

    def __setitem__(self, key, item) -> None:
        """
        Set the given location to the Sentence.

        Args:
            key: The location in the Conll file to set to the given sentence.
                This accepts integer or slice keys and accepts negative indexing.
            item: The item to insert. This can be an individual sentence, or
                another Conll object.
        """
        self._sentences[key] = item

    def __delitem__(self, key: Union[int, slice]) -> None:
        """
        Delete the Sentence corresponding with the given key.

        Args:
            key: The info to get the Sentence to delete. Can be the integer
                position in the file, or a slice.
        """
        del self._sentences[key]

    def __len__(self) -> int:
        """
        Returns the number of sentences in the CoNLL-U file.

        Returns:
            The size of the CoNLL-U file in sentences.
        """
        return len(self._sentences)
