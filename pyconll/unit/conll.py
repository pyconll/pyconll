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
        self._ids_to_indexes = {}

        for sentence in pyconll._parser.iter_sentences(it):
            if sentence.id is not None:
                self._sentences.append(sentence)
                self._ids_to_indexes[sentence.id] = len(self._sentences) - 1

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
        sentences if the key is a slice in the form of another Conll object.
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

                sliced_conll = Conll([])
                sliced_conll._sentences = self._sentences[start_idx:stop_idx:
                                                          key.step]
                for i, sentence in enumerate(sliced_conll._sentences):
                    if sentence.id is not None:
                        sliced_conll._ids_to_indexes[sentence.id] = i

                return sliced_conll

    def __setitem__(self, key, sent):
        """
        Set the given location to the Sentence.

        Args:
        key: The location in the Conll file to set to the given sentence. This
            only accepts integer keys.
        """
        old_id = self._sentences[key].id
        del self._ids_to_indexes[old_id]

        self._sentences[key] = sent
        self._ids_to_indexes[sent.id] = key

    def __delitem__(self, key):
        """
        Delete the Sentence corresponding with the given key.

        Args:
        key: The info to get the Sentence to delete. Can be the integer position
            in the file, the sentence id, or a slice, where the slice can have
            either id or integer start and stop.
        """
        if isinstance(key, slice):
            if isinstance(key.start, int):
                idx_start = key.start
                idx_end = key.stop
            else:
                idx_start = self._ids_to_indexes[key.start]
                idx_end = self._ids_to_indexes[key.stop]

            for sentence in self._sentences[idx_start:idx_end]:
                del self._ids_to_indexes[sentence.id]

            del self._sentences[idx_start:idx_end:key.step]
        else:
            if isinstance(key, int):
                idx = key
                sent_id = self._sentences[key].id
            elif isinstance(key, str):
                idx = self._ids_to_indexes[key]
                sent_id = key

            del self._sentences[idx]
            del self._ids_to_indexes[sent_id]

    def __len__(self):
        """
        Returns the number of sentences in the CoNLL-U file.

        Returns:
        The size of the CoNLL-U file in sentences.
        """
        return len(self._sentences)
