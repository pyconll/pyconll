import operator
import re

from pyconllu.unit import Token


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
    lines that provide annotation to the text provided.
    """

    COMMENT_MARKER = '#'
    KEY_VALUE_COMMENT_PATTERN = COMMENT_MARKER + r'\s*(\S+)\s*=\s*(\S+)'
    SINGLETON_COMMENT_PATTERN = COMMENT_MARKER + r'\s*(\S+)$'

    SENTENCE_ID_KEY = 'sent_id'

    def __init__(self, conllu_s):
        """
        Construct a Sentence object from the provided CoNLL-U string.

        Args:
        conllu_s: The raw CoNLL-U string to parse. Comments must precede token
            lines.
        """
        self._source = conllu_s
        lines = conllu_s.split('\n')

        # Assign defaults to id and text now, and then reassign them if they
        # exist.
        self._id = None
        self._text = None

        self.meta = {}
        self.tokens = []
        for line in lines:
            if line[0] == Sentence.COMMENT_MARKER:
                kv_match = re.match(Sentence.KEY_VALUE_COMMENT_PATTERN, line)
                singleton_match = re.match(Sentence.SINGLETON_COMMENT_PATTERN,
                                           line)

                if kv_match:
                    k = kv_match.group(1)
                    v = kv_match.group(2)
                    self.meta[k] = v
                elif singleton_match:
                    k = kv_match.group(1)
                    self.meta[k] = None
            else:
                token = Token(line)
                self.tokens.append(token)

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
        return ' '.join([token.form for token in self.tokens])

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

        for token in self.tokens:
            lines.append(token.conllu())

        return '\n'.join(lines)
