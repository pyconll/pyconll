from pyconllu.unit import Sentence

class Conllu:
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
        """

        self._sentences = []
        self._id_to_indexes = {}

        sent_lines = []
        for line in it:
            line = line.strip()

            # Collect all lines until there is a blank line. Then all the
            # collected lines were between blank lines and are a sentence.
            if line:
                sent_lines.append(line)
            else:
                sent_source = '\n'.join(sent_lines)
                sentence = Sentence(sent_source)
                sent_lines.clear()

                self._sentences.append(sentence)

                if sentence.id is not None:
                    self._id_to_indexes[sentence.id] = len(self._sentences) - 1

    def __iter__(self):
        """
        """
        for sentence in self._sentences:
            yield sentence

    def __getitem__(self, key):
        """
        """
        if isinstance(key, str):
            idx = self._id_to_indexes[key]
            return self._sentences[idx]
        elif isinstance(key, int):
            return self._sentences[key]
        else:
            if isinstance(key.start, int):
                return self._sentences[key.start:key.stop:key.step]
            elif isinstance(key.start, str):
                start_idx = self._id_to_indexes[key.start]
                stop_idx = self._id_to_indexes[key.stop]

                return self._sentences[start_idx:stop_idx:key.step]

    def __len__(self):
        """
        """
        return len(self._sentences)
