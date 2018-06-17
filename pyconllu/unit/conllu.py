import itertools

from pyconllu.unit import Sentence
import pyconllu._parser


class Conllu:
    """
    The abstraction for a CoNLL-U file. A CoNLL-U file is more or less just a
    collection of sentences in order. These sentences can be accessed by
    sentence id or by numeric index. Note that sentences must be separated by
    whitespace. CoNLL-U also specifies that the file must end in a new line but
    that requirement is relaxed here in parsing.
    """

    def __init__(self, it):
        # Replacing from ... import syntax with this semi equivalent.
        #iter_sentences = pyconllu._parser.iter_sentences
        """
        Create a CoNLL-U file collection of sentences.

        Args:
        it: An iterator of the lines of the CoNLL-U file.
        """
        self._sentences = []
        self._ids_to_indexes = {}

        for sentence in pyconllu._parser.iter_sentences(it):
            if sentence.id is not None:
                self._sentences.append(sentence)
                self._ids_to_indexes[sentence.id] = len(self._sentences) - 1

    def conllu(self):
        """
        Output the Conllu object to a CoNLL-U formatted string.

        Returns:
        The CoNLL-U object as a string. This string will end in a newline.
        """
        # Add newlines along with sentence strings so that there is no need to
        # slice potentially long lists or modify strings.
        components = []
        for sentence in self._sentences:
            components.append(sentence.conllu())
            components.append('\n\n')

        return ''.join(components)

    def write(self, writable):
        """
        Write the Conllu object to something that is writable.

        For simply writing, this method is more efficient than calling conllu
        then writing since no string of the entire Conllu object is created. The
        final output will include a final newline.

        Args:
        writable: The writable object such as a file. Must have a write method.
        """
        for sentence in self._sentences:
            writable.write(sentence.conllu())
            writable.write('\n\n')

    def conllu(self):
        """
        Output the Conllu object to a CoNLL-U formatted string.

        Returns:
        The CoNLL-U object as a string. This string will end in a newline.
        """
        # Add newlines along with sentence strings so that there is no need to
        # slice potentially long lists or modify strings.
        components = []
        for sentence in self._sentences:
            components.append(sentence.conllu())
            components.append('\n\n')

        return ''.join(components)

    def write(self, writable):
        """
        Write the Conllu object to something that is writable.

        For simply writing, this method is more efficient than calling conllu
        then writing since no string of the entire Conllu object is created. The
        final output will include a final newline.

        Args:
        writable: The writable object such as a file. Must have a write method.
        """
        for sentence in self._sentences:
            writable.write(sentence.conllu())
            writable.write('\n\n')

    def __iter__(self):
        """
        Allows for iteration over every sentence in the CoNLL-U file.
        """
        for sentence in self._sentences:
            yield sentence

    def __getitem__(self, key):
        """
        Index a sentence by key value.

        Args:
        key: The key to index the sentence by. This key can either be a numeric
        key, the sentence id, or a slice.

        Returns:
        The corresponding sentence if the key is an int or string or the
        sentences if the key is a slice in the form of another Conllu object.
        """
        if isinstance(key, int):
            return self._sentences[key]
        elif isinstance(key, str):
            idx = self._ids_to_indexes[key]
            return self._sentences[idx]
        else:
            if isinstance(key.start, int):
                return self._sentences[key.start:key.stop:key.step]
            elif isinstance(key.start, str):
                start_idx = self._ids_to_indexes[key.start]
                stop_idx = self._ids_to_indexes[key.stop]

                sliced_conllu = Conllu([])
                sliced_conllu._sentences = self._sentences[start_idx:stop_idx:
                                                           key.step]
                for i, sentence in enumerate(sliced_conllu._sentences):
                    if sentence.id is not None:
                        sliced_conllu._ids_to_indexes[sentence.id] = i

                return sliced_conllu

    def __len__(self):
        """
        Returns the number of sentences in the CoNLL-U file.

        Returns:
        The size of the CoNLL-U file in sentences.
        """
        return len(self._sentences)
