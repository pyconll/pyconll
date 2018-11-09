"""
Create the SentenceTree type as a wrapper around a sentence that constructs a
tree as well to traverse the sentence in a new way.
"""

from pyconll.conllable import Conllable

from . import Tree


class SentenceTree(Conllable):
    """
    A Tree wrapper around a sentence. This type will take in an existing serial
    sentence, and create a tree representation from it. This type holds both the
    sentence and the tree representation of the sentence. Note that an empty
    sentence input will have no data and no children.
    """

    @staticmethod
    def _create_tree(sentence, root, children_tokens):
        """
        Method to create a tree from a sentence given the root token.

        Args:
            sentence: The sentence to construct the tree from.
            root: The root token to start the tree at.
            children_tokens: A dictionary from token id to children tokens.

        Returns:
            A Tree constructed given the sentence structure.
        """
        try:
            tokens = children_tokens[root.id]
            trees = list(
                map(
                    lambda token: SentenceTree._create_tree(sentence, token, children_tokens),
                    tokens))
        except KeyError:
            trees = None

        return Tree(sentence[root.id], trees)

    def __init__(self, sentence):
        """
        Creates a new SentenceTree given the sentence.

        Args:
            sentence: The sentence to wrap and construct a tree from.
        """
        self._sentence = sentence
        children_tokens = {}

        root_token = None
        for token in self.sentence:
            parent_key = token.head

            try:
                children_tokens[parent_key].append(token)
            except KeyError:
                children_tokens[parent_key] = [token]

            if token.head == '0':
                root_token = token

        root = SentenceTree._create_tree(self.sentence, root_token, children_tokens) \
                    if root_token else Tree(root_token, None)

        self._tree = root

    @property
    def sentence(self):
        """
        Provides the unwrapped sentence. This property is readonly.

        Returns:
            The unwrapped sentence.
        """
        return self._sentence

    @property
    def tree(self):
        """
        Provides the constructed tree. This property is readonly.

        Returns:
            The constructed tree.
        """
        return self._tree

    def conll(self):
        """
        Outputs the provided tree into CoNLL format.

        Returns:
            The CoNLL formatted string.
        """
        return self.sentence.conll()
