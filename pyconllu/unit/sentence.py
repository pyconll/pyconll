import operator
import re

from pyconllu.unit import Token


def _same_type_hierarchy(obj1, obj2):
    """
    Checks if two objects are within the same type hierarhcy.

    Args:
    obj1: The first object.
    obj2: The second object.

    Returns:
    True if the two objects are in the same type hierarchy, obj1 inherits / is-a
    from obj2 or vice-versa.
    """
    return isinstance(obj1, obj2) or isinstance(obj2, obj1)


class Sentence:
    """
    A sentence in a CoNLL-U file. A sentence consists of several components.

    First, are comments. Each sentence must have two comments per UD v2
    guidelines, which are sent_id and text. While this class does not have this
    requirement, a sent_id or text comment must have the correct structure. This
    means no ':' instead of '='. Comments are stored as a dict in the meta
    field. For singleton comments with no key-value structure, the value in the
    dict has a value of None.

    Note the sent_id field is also assigned to the id property for usability.
    Also note that to get the current text of the Sentence, use the text
    property. The value in the meta dict is not updated as tokens change and so
    will not be current. The id field will be None if to start if there is no
    id comment. The text field will never be None to start and instead computes
    the text each time from the tokens.

    TODO: This use of fields seems somewhat complicated. There may be a clearer
    way.

    Then second, are the token lines. Each sentence is made up of many token
    lines that provide annotation to the text provided. While a sentence usually
    means a collection of tokens, in this CoNLL-U since, it is more useful to
    think of it as a collection of annotations with some associated metadata.
    """

    COMMENT_MARKER = '#'
    KEY_VALUE_COMMENT_PATTERN = COMMENT_MARKER + r'\s*(\S+)\s*=\s*(.+)'
    SINGLETON_COMMENT_PATTERN = COMMENT_MARKER + r'\s*(\S+)$'

    SENTENCE_ID_KEY = 'sent_id'

    def __init__(self, source, doc=None, par=None):
        """
        Construct a Sentence object from the provided CoNLL-U string.

        Args:
        source: The raw CoNLL-U string to parse. Comments must precede token
            lines.
        """
        self.source = source
        lines = self.source.split('\n')

        # Assign defaults to id and text now, and then reassign them if they
        # exist.
        self._id = None
        self._text = None

        self.meta = {}
        self._tokens = []
        self._ids_to_indexes = {}

        for line in lines:
            if line:
                if line[0] == Sentence.COMMENT_MARKER:
                    kv_match = re.match(Sentence.KEY_VALUE_COMMENT_PATTERN,
                                        line)
                    singleton_match = re.match(
                        Sentence.SINGLETON_COMMENT_PATTERN, line)

                    if kv_match:
                        k = kv_match.group(1)
                        v = kv_match.group(2)
                        self.meta[k] = v
                    elif singleton_match:
                        k = kv_match.group(1)
                        self.meta[k] = None
                else:
                    token = Token(line)
                    self._tokens.append(token)

                    if token.id is not None:
                        self._ids_to_indexes[token.id] = len(self._tokens) - 1

        # TODO: keep track of whitespace here.

        if Sentence.SENTENCE_ID_KEY in self.meta:
            self._id = self.meta[Sentence.SENTENCE_ID_KEY]

    @property
    def id(self):
        """
        Get the sentence id.

        Returns:
        The sentence id.
        """
        return self._id

    @id.setter
    def id(self, new_id):
        """
        Set the sentence id.

        Args:
        new_id: The new id of this sentence.
        """
        self.meta[Sentence.SENTENCE_ID_KEY] = new_id
        self._id = new_id

    @property
    def text(self):
        """
        Get the continuous text for this sentence. Read-only.

        Returns;
        The continuous text of this sentence.
        """
        # TODO: Better compute the text representation.
        return ' '.join([token.form for token in self._tokens])

    def conllu(self, include_text=True):
        """
        Convert the sentence to a CoNLL-U representation.

        Args:
        include_text: Flag to indicate if the output should include a comment
            for the text.

        Returns:
        A string representing the Sentence in CoNLL-U format.
        """
        lines = []
        sorted_meta = sorted(self.meta.items(), key=operator.itemgetter(0))
        for meta in sorted_meta:
            if meta[1] is not None:
                line = '{} {} = {}'.format(Sentence.COMMENT_MARKER, meta[0],
                                           meta[1])
            else:
                line = '{} {}'.format(Sentence.COMMENT_MARKER, meta[0])

        for token in self._tokens:
            lines.append(token.conllu())

        return '\n'.join(lines)

    def append_token(self, token):
        """
        """
        self._tokens.append(token)

        if token.id is not None:
            self._ids_to_indexes[token.id] = len(self._tokens) - 1

    def insert_token(self, i, token):
        """
        Insert a token into the given location in this sentence.
        """
        if isinstance(i, str):
            start = self._ids_to_indexes[i] + 1
        else:
            start = i + 1

        self._tokens.insert(i, token)
        self._ids_to_indexes[token.id] = i

        for t in self._tokens[start:]:
            self._ids_to_indexes[t.id] += 1

    def __iter__(self):
        """
        Iterate through all the tokens in the Sentence including multiword tokens.
        """
        for token in self._tokens:
            yield token

    def __getitem__(self, key):
        """
        Return the desired tokens from the Sentence.
        """
        if isinstance(key, str):
            idx = self._ids_to_indexes[key]
            return self._tokens[idx]
        elif isinstance(key, int):
            return self._tokens[key]
        elif isinstance(key, slice):
            proper_types = isinstance(key.start, key.stop) or \
                isinstance(key.stop, key.start) and \
                isinstance(key.start, (str, int)) and \
                (key.step is None or isinstance(key.step, int))

            if proper_types:
                if isinstance(key.start, str):
                    start_idx = self._ids_to_indexes[key.start]
                    end_idx = self._ids_toindexes[key.end]

                    return self._tokens[start_idx:end_idx:key.step]
            else:
                raise ValueError(
                    'Start and stop must both be strings or integers and step must be integer'
                )

    def __setitem__(self, key, value):
        """
        Set the specified location to the desired token.

        Args:
        key: The location of the token. Can be an integer or a string id.
        value: The token to store.

        Raises:
        ValueError: If the key is not an integer or string id or if the value is not a token.
        """
        if isinstance(value, Token) and isinstance(value, (int, str)):
            if isinstance(value, int):
                self._tokens[key] = value
            else:
                idx = self._ids_to_indexes[key]
                self._tokens[idx] = value
        else:
            raise ValueError('Sentence units can only be tokens')

    def __delitem__(self, key):
        """
        Delete token associated with the key.

        Args:
        key: The associated token. The token can be an integer, string id, or
            slice.
        """
        if isinstance(key, int):
            del self.tokens[key]
        elif isinstance(key, str):
            idx = self._ids_to_indexes[key]
            del self.tokens[idx]
        elif isinstance(key, slice):
            if _same_type_hierarchy(key.start, key.stop):
                if isinstance(key, str):
                    start = self._ids_to_indexes[key.start]
                    stop = self._ids_to_indexes[key.stop]
                else:
                    start = key.start
                    stop = key.stop

                del self._tokens[start:stop:key.step]
        else:
            raise ValueError('key must be a integer, string, or slice.')

    def __len__(self):
        """
        Get the length of this sentence.

        Returns:
        The amount of tokens in this sentence. In the CoNLL-U sense, this
        includes both all the multiword tokens and their decompositions.
        """
        return len(self._tokens)
