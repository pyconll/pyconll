"""
Create the SentenceTree type as a wrapper around a sentence that constructs a
tree as well to traverse the sentence in a new way.
"""

from pyconll.conllable import Conllable

from . import Tree, TreeBuilder


class SentenceTree(Conllable):
    """
    A Tree wrapper around a sentence. This type will take in an existing serial
    sentence, and create a tree representation from it. This type holds both the
    sentence and the tree representation of the sentence. Note that an empty
    sentence input will have no data and no children.
    """

    @staticmethod
    def _create_tree_helper(builder, sentence, root, children_tokens):
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
            SentenceTree._create_tree_helper(builder, sentence, token,
                                             children_tokens)
            builder.move_to_parent()

    @staticmethod
    def _create_tree(sentence):
        """
        Creates a new Tree from the provided sentence.

        Args:
            sentence: The sentence to create a Tree representation of.

        Returns:
            A constructed Tree that represents the dependencies in the sentence.
        """
        children_tokens = {}

        root_token = None
        for token in sentence:
            parent_key = token.head

            try:
                children_tokens[parent_key].append(token)
            except KeyError:
                children_tokens[parent_key] = [token]

            if token.head == '0':
                root_token = token

        builder = TreeBuilder()
        builder.create_root(root_token)
        if root_token:
            SentenceTree._create_tree_helper(builder, sentence, root_token,
                                             children_tokens)
        root = builder.build()

        return root

    def __init__(self, sentence):
        """
        Creates a new SentenceTree given the sentence.

        Args:
            sentence: The sentence to wrap and construct a tree from.
        """
        self._sentence = sentence
        self._tree = SentenceTree._create_tree(sentence)

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
        Outputs the tree into CoNLL format.

        Returns:
            The CoNLL formatted string.
        """
        return self.sentence.conll()
