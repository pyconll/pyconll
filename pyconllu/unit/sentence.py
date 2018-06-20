import operator
import re

from pyconllu.unit import Token


class Sentence:
    """
    A sentence in a CoNLL-U file. A sentence consists of several components.

    First, are comments. Each sentence must have two comments per UD v2
    guidelines, which are sent_id and text. Comments are stored as a dict in
    the meta field. For singleton comments with no key-value structure, the
    value in the dict has a value of None.

    Note the sent_id field is also assigned to the id property, and the text
    field is assigned to the text property for usability, and their importance
    as comments. The text property is read only.

    Then comes the token annotations. Each sentence is made up of many token
    lines that provide annotation to the text provided. While a sentence usually
    means a collection of tokens, in this CoNLL-U sense, it is more useful to
    think of it as a collection of annotations with some associated metadata.
    Therefore the text of the sentence cannot be changed with this class, only
    the associated annotations can be changed.
    """

    COMMENT_MARKER = '#'
    KEY_VALUE_COMMENT_PATTERN = COMMENT_MARKER + r'\s*([^=]+?)\s*=\s*(.+)'
    SINGLETON_COMMENT_PATTERN = COMMENT_MARKER + r'\s*(\S+)$'

    SENTENCE_ID_KEY = 'sent_id'
    TEXT_KEY = 'text'

    # TODO: How to handle doc and par.
    def __init__(self, source, _start_line_number=None, _end_line_number=None):
        """
        Construct a Sentence object from the provided CoNLL-U string.

        Args:
        source: The raw CoNLL-U string to parse. Comments must precede token
            lines.
        _start_line_number: The starting line of the sentence. Mostly for
            internal use.
        _end_line_number: The ending line of the sentence. Mostly for internal
            use.
        """
        self.source = source
        lines = self.source.split('\n')

        self.start_line_number = _start_line_number
        self.end_line_number = _end_line_number

        self._meta = {}
        self._tokens = []
        self._ids_to_indexes = {}

        for i, line in enumerate(lines):
            if line:
                if line[0] == Sentence.COMMENT_MARKER:
                    kv_match = re.match(Sentence.KEY_VALUE_COMMENT_PATTERN,
                                        line)
                    singleton_match = re.match(
                        Sentence.SINGLETON_COMMENT_PATTERN, line)

                    if kv_match:
                        k = kv_match.group(1)
                        v = kv_match.group(2)
                        self._meta[k] = v
                    elif singleton_match:
                        k = singleton_match.group(1)
                        self._meta[k] = None
                else:
                    # If there is a line number for the sentence, then include
                    # the line number for the token.
                    if self.start_line_number:
                        token = Token(
                            line, _line_number=self.start_line_number + i)
                    else:
                        token = Token(line)

                    self._tokens.append(token)

                    if token.id is not None:
                        self._ids_to_indexes[token.id] = len(self._tokens) - 1

    @property
    def id(self):
        """
        Get the sentence id.

        Returns:
        The sentence id.
        """
        return self._meta[Sentence.SENTENCE_ID_KEY]

    @id.setter
    def id(self, new_id):
        """
        Set the sentence id.

        Args:
        new_id: The new id of this sentence.
        """
        self._meta[Sentence.SENTENCE_ID_KEY] = new_id

    @property
    def text(self):
        """
        Get the continuous text for this sentence. Read-only.

        Returns;
        The continuous text of this sentence.
        """
        return self._meta[Sentence.TEXT_KEY]

    def meta_value(self, key):
        """
        Returns the value associated with the key in the metadata (comments).

        Args:
        key: The key whose value to look up.

        Returns:
        The value associated with the key as a string. If the key is not present
        then a KeyError is thrown, and if the key is a singleton then None is
        returned.
        """
        return self._meta[key]

    def meta_present(self, key):
        """
        Check if the key is present as a singleton or as a pair.

        Args:
        key: The value to check for in the comments.

        Returns:
        True if the key was provided as a singleton or as a key value pair.
        False otherwise.
        """
        return key in self._meta

    def conllu(self):
        """
        Convert the sentence to a CoNLL-U representation.

        Returns:
        A string representing the Sentence in CoNLL-U format.
        """
        lines = []
        sorted_meta = sorted(self._meta.items(), key=operator.itemgetter(0))
        for meta in sorted_meta:
            if meta[1] is not None:
                line = '{} {} = {}'.format(Sentence.COMMENT_MARKER, meta[0],
                                           meta[1])
            else:
                line = '{} {}'.format(Sentence.COMMENT_MARKER, meta[0])

            lines.append(line)

        for token in self._tokens:
            lines.append(token.conllu())

        return '\n'.join(lines)

    def __iter__(self):
        """
        Iterate through all the tokens in the Sentence including multiword tokens.
        """
        for token in self._tokens:
            yield token

    def __getitem__(self, key):
        """
        Return the desired tokens from the Sentence.

        Returns:
        If the key is a string then the appropriate Token. The key can also be
        a slice in which case a list of tokens is provided.
        """
        if isinstance(key, str):
            idx = self._ids_to_indexes[key]
            return self._tokens[idx]
        elif isinstance(key, slice):
            start_idx = self._ids_to_indexes[key.start]
            end_idx = self._ids_toindexes[key.end]

            return self._tokens[start_idx:end_idx:key.step]

    def __len__(self):
        """
        Get the length of this sentence.

        Returns:
        The amount of tokens in this sentence. In the CoNLL-U sense, this
        includes both all the multiword tokens and their decompositions.
        """
        return len(self._tokens)
