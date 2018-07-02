import collections
import itertools

import pyconll._parser
from pyconll.unit import Sentence


class Conll:
    """
    The abstraction for a CoNLL-U file. A CoNLL-U file is more or less just a
    collection of sentences in order. These sentences can be accessed by
    sentence id or by numeric index. Note that sentences must be separated by
    whitespace. CoNLL-U also specifies that the file must end in a new line but
    that requirement is relaxed here in parsing.
    """

    def __init__(self, it):
        """
        Create a CoNLL-U file collection of sentences.

        Args:
        it: An iterator of the lines of the CoNLL-U file.
        with_lines: An optional flag indicating to include line numbers when
            constructing Sentences. If set, the Sentences will have a start and
            end line number, and Tokens will have a line number.
        """
        self._sentences = []
        self._ids_to_indexes = collections.defaultdict(set)

        for sentence in pyconll._parser.iter_sentences(it):
            if sentence.id is not None:
                self._sentences.append(sentence)
                self._ids_to_indexes[sentence.id].add(len(self._sentences) - 1)

    def conll(self):
        """
        Output the Conll object to a CoNLL-U formatted string.

        Returns:
        The CoNLL-U object as a string. This string will end in a newline.
        """
        # Add newlines along with sentence strings so that there is no need to
        # slice potentially long lists or modify strings.
        components = []
        for sentence in self._sentences:
            components.append(sentence.conll())
            components.append('\n\n')

        return ''.join(components)

    def write(self, writable):
        """
        Write the Conll object to something that is writable.

        For simply writing, this method is more efficient than calling conll
        then writing since no string of the entire Conll object is created. The
        final output will include a final newline.

        Args:
        writable: The writable object such as a file. Must have a write method.
        """
        for sentence in self._sentences:
            writable.write(sentence.conll())
            writable.write('\n\n')

    def append(self, sent):
        """
        Add the given sentence to the end of this Conll object.

        Args:
        sent: The Sentence object to add.
        """
        self._sentences.append(sent)
        self._ids_to_indexes[sent.id].add(len(self._sentences) - 1)

    def insert(self, index, sent):
        """
        Insert the given sentence into the given location.

        Args:
        index: The numeric index to insert the sentence into.
        sent: The sentence to insert.
        """
        self._sentences.insert(index, sent)

        for idx, sent in enumerate(self._sentences[index:]):
            self._ids_to_indexes[sent.id] = idx

    def __contains__(self, sent):
        """
        Check if the Conll object has this sentence.

        Args:
        sent: The sentence to check for.

        Returns:
        True if this Sentence is exactly in the Conll object. False, otherwise.
        """
        try:
            sent_ids = self._ids_to_indexes[sent.id]

            equal = False
            for id in sent_ids:
                equal = equal or sent == self[sent_id]
        except KeyError:
            return False

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
        key, or a slice.

        Returns:
        The corresponding sentence if the key is an int or the sentences if the
        key is a slice in the form of another Conll object.
        """
        if isinstance(key, int):
            return self._sentences[key]
        else:
            sliced_conll = Conll([])
            sliced_conll._sentences = self._sentences[key.start:key.stop:
                                                      key.step]
            for i, sentence in enumerate(sliced_conll._sentences):
                if sentence.id is not None:
                    sliced_conll._ids_to_indexes[sentence.id].add(i)

            return sliced_conll

    def __setitem__(self, key, sent):
        """
        Set the given location to the Sentence.

        Args:
        key: The location in the Conll file to set to the given sentence. This
            only accepts integer keys.
        """
        old_id = self._sentences[key].id
        self._ids_to_indexes[old_id].remove(key)

        self._sentences[key] = sent
        self._ids_to_indexes[sent.id].add(key)

    def __delitem__(self, key):
        """
        Delete the Sentence corresponding with the given key.

        Args:
        key: The info to get the Sentence to delete. Can be the integer position
            in the file, or a slice.
        """
        if isinstance(key, slice):
            for i, sentence in enumerate(
                    self._sentences[key.start:key.stop:key.stop]):
                idx = i + key.start
                self._ids_to_indexes[sentence.id].remove(idx)

            del self._sentences[key.start:key.stop:key.step]
        else:
            sent_id = self._sentences[key].id

            del self._sentences[key]
            self._ids_to_indexes[sent_id].remove(key)

    def __len__(self):
        """
        Returns the number of sentences in the CoNLL-U file.

        Returns:
        The size of the CoNLL-U file in sentences.
        """
        return len(self._sentences)
