"""
Defines the Sentence type and the associated parsing and output logic.
"""

import operator
import re
from typing import Dict, Iterator, List, Optional, Sequence, overload

from pyconll.conllable import Conllable
from pyconll.tree._treebuilder import TreeBuilder
from pyconll.tree.tree import Tree
from pyconll.unit.token import Token


class Sentence(Sequence[Token], Conllable):
    """
    A sentence in a CoNLL-U file. A sentence consists of several components.

    First, are comments. Each sentence must have two comments per UD v2
    guidelines, which are sent_id and text. Comments are stored as a dict in
    the meta field. For singleton comments with no key-value structure, the
    value in the dict has a value of None.

    Note the sent_id field is also assigned to the id property, and the text
    field is assigned to the text property for usability, and their importance
    as comments. The text property is read only along with the paragraph and
    document id. This is because the paragraph and document id are not defined
    per Sentence but across multiple sentences. Instead, these fields can be
    changed through changing the metadata of the Sentences.

    Then comes the token annotations. Each sentence is made up of many token
    lines that provide annotation to the text provided. While a sentence usually
    means a collection of tokens, in this CoNLL-U sense, it is more useful to
    think of it as a collection of annotations with some associated metadata.
    Therefore the text of the sentence cannot be changed with this class, only
    the associated annotations can be changed.
    """

    __slots__ = ['_meta', '_tokens', '_ids_to_indexes']

    COMMENT_MARKER = '#'
    KEY_VALUE_COMMENT_PATTERN = COMMENT_MARKER + r'\s*([^=]+?)\s*=\s*(.+)'
    SINGLETON_COMMENT_PATTERN = COMMENT_MARKER + r'\s*(\S.*?)\s*$'

    SENTENCE_ID_KEY = 'sent_id'
    TEXT_KEY = 'text'

    def __init__(self, source: str) -> None:
        """
        Construct a Sentence object from the provided CoNLL-U string.

        Args:
            source: The raw CoNLL-U string to parse. Comments must precede token
                lines.

        Raises:
            ParseError: If there is any token that was not valid.
        """
        lines = source.split('\n')

        self._meta: Dict[str, Optional[str]] = {}
        self._tokens: List[Token] = []
        self._ids_to_indexes: Dict[str, int] = {}

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
                        self._meta[k] = v
                    elif singleton_match:
                        k = singleton_match.group(1)
                        self._meta[k] = None
                else:
                    token = Token(line)
                    self._tokens.append(token)

                    if token.id is not None:
                        self._ids_to_indexes[token.id] = len(self._tokens) - 1

    @property
    def id(self) -> Optional[str]:
        """
        Get the sentence id.

        Returns:
            The sentence id. If there is none, then returns None.
        """
        try:
            return self._meta[Sentence.SENTENCE_ID_KEY]
        except KeyError:
            return None

    @id.setter
    def id(self, new_id: str) -> None:
        """
        Set the sentence id.

        Args:
            new_id: The new id of this sentence.
        """
        self._meta[Sentence.SENTENCE_ID_KEY] = new_id

    @property
    def text(self) -> Optional[str]:
        """
        Get the continuous text for this sentence. Read-only.

        Returns:
            The continuous text of this sentence. If none is provided in
            comments, then None is returned.
        """
        try:
            return self._meta[Sentence.TEXT_KEY]
        except KeyError:
            return None

    def meta_value(self, key: str) -> Optional[str]:
        """
        Returns the value associated with the key in the metadata (comments).

        Args:
            key: The key whose value to look up.

        Returns:
            The value associated with the key as a string. If the key is a
            singleton then None is returned.

        Raises:
            KeyError: If the key is not present in the comments.
        """
        return self._meta[key]

    def meta_present(self, key: str) -> bool:
        """
        Check if the key is present as a singleton or as a pair.

        Args:
            key: The value to check for in the comments.

        Returns:
            True if the key was provided as a singleton or as a key value pair.
            False otherwise.
        """
        return key in self._meta

    def set_meta(self, key: str, value: Optional[str] = None) -> None:
        """
        Set or add the metadata or comments associated with this Sentence.

        Args:
            key: The key for the comment.
            value: The value to associate with the key. If the comment is a
                singleton, this field can be ignored or set to None.
        """
        if key == Sentence.TEXT_KEY:
            raise ValueError('Key cannot be {}'.format(Sentence.TEXT_KEY))

        self._meta[key] = value

    def remove_meta(self, key: str) -> None:
        """
        Remove a metadata element associated with the Sentence.

        Args:
            key: The name of the metadata / comment.

        Raises:
            KeyError: If the key is not present in the Sentence metadata.
            ValueError: If the text key is provided, regardless of presence.
        """
        if key == Sentence.TEXT_KEY:
            raise ValueError('Key cannot be {}'.format(Sentence.TEXT_KEY))

        del self._meta[key]

    def to_tree(self) -> Tree[Token]:
        """
        Creates a Tree data structure from the current sentence.

        An empty sentence will cannot be converted into a Tree and will throw an
        exception. The children for a node in the tree are ordered as they
        appear in the sentence. So the earliest child of a token appears first
        in the token's children in the tree.

        Each Tree node has a data member that references the actual Token
        represented by the node. Multiword tokens are not included in the tree
        since they are more like virtual Tokens and do not participate in any
        dependency relationships or carry much value in dependency relations.

        Returns:
            A constructed Tree that represents the dependency graph of the
            sentence.

        Raises:
            ValueError: If the sentence can not be made into a tree because a
                token has an empty head value or if there is no root token.
        """
        children_tokens: Dict[str, List[Token]] = {}

        for token in self:
            if token.head is not None:
                try:
                    children_tokens[token.head].append(token)
                except KeyError:
                    children_tokens[token.head] = [token]
            elif not token.is_multiword():
                raise ValueError(
                    'The current sentence is not fully defined as a tree and ' \
                    'has a token with an empty head at {}'.format(token.id))

        builder: TreeBuilder[Token] = TreeBuilder()
        if '0' in children_tokens:
            if len(children_tokens['0']) != 1:
                raise ValueError(
                    'There should be exactly one root token in a sentence.')

            root_token = children_tokens['0'][0]
            builder.create_root(root_token)
            Sentence._create_tree_helper(builder, self, root_token,
                                         children_tokens)
        else:
            raise ValueError('The current sentence has no root token.')

        root = builder.build()
        return root

    @staticmethod
    def _create_tree_helper(builder: TreeBuilder, sentence: 'Sentence',
                            root: Token,
                            children_tokens: Dict[str, List[Token]]) -> None:
        """
        Method to create a tree from a sentence given the root token.

        Args:
            builder: The TreeBuilder currently being used to create the Tree.
            sentence: The sentence to construct the tree from.
            root: The current token we are constructing the tree at.
            children_tokens: A dictionary from token id to children tokens.

        Returns:
            A Tree constructed given the sentence structure.
        """
        try:
            tokens = children_tokens[root.id]
        except KeyError:
            tokens = []

        for token in tokens:
            builder.add_child(data=token, move=True)
            Sentence._create_tree_helper(builder, sentence, token,
                                         children_tokens)
            builder.move_to_parent()

    def conll(self) -> str:
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
            lines.append(token.conll())

        return '\n'.join(lines)

    def __iter__(self) -> Iterator[Token]:
        """
        Iterate through all the tokens in the Sentence including multiword
        tokens.
        """
        for token in self._tokens:
            yield token

    @overload
    def __getitem__(self, key: str) -> Token:
        pass

    @overload
    def __getitem__(self, key: int) -> Token:
        pass

    @overload
    def __getitem__(self, key: slice) -> Sequence[Token]:
        pass

    def __getitem__(self, key):
        """
        Return the desired tokens from the Sentence.

        Args:
            key: The indicator for the tokens to return. Can either be an
                integer, a string, or a slice. For an integer, the numeric
                indexes of Tokens are used. For a string, the id of the Token is
                used. And for a slice the start and end must be the same data
                types, and can be both string and integer.

        Returns:
            If the key is a string then the appropriate Token. The key can also
            be a slice in which case a sequence of tokens is provided.
        """
        if isinstance(key, str):
            idx = self._ids_to_indexes[key]
            return self._tokens[idx]

        if isinstance(key, int):
            return self._tokens[key]

        if isinstance(key, slice):
            if isinstance(key.start, str):
                start_idx = self._ids_to_indexes[key.start]
            else:
                start_idx = key.start

            if isinstance(key.stop, str):
                end_idx = self._ids_to_indexes[key.stop]
            else:
                end_idx = key.stop

            return self._tokens[start_idx:end_idx:key.step]

        raise ValueError('The key must be a str, int, or slice.')

    def __len__(self) -> int:
        """
        Get the length of this sentence.

        Returns:
            The amount of tokens in this sentence. In the CoNLL-U sense, this
            includes both all the multiword tokens and their decompositions.
        """
        return len(self._tokens)
