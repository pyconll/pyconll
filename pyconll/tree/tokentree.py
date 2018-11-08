"""
Creates a TokenTree type which creates a Tree from a provided Sentence.
"""

from . import Tree


class TokenTree(Tree):
    """
    A Tree to represent a string of tokens, or a sentence. This class constructs
    a Tree structure given a Sentence, with the root token as the root of the
    tree. The token is on the token attribute of the tree. Note that changing
    the head field of a token in a tree is not supported, and a tree will have
    to be regenerated in that case.
    """

    @staticmethod
    def _create_tree(sentence, root, children_tokens):
        """
        Creates a new TokenTree given the original Sentence and the root token.

        Args:
            sentence: The wrapped sentence.
            root: The root token for the created tree.
            children_tokens: A dictionary mapping token ids to token children.

        Returns:
            The final constructed tree with root at its root.
        """
        try:
            tokens = children_tokens[root.id]
            trees = list(
                map(
                    lambda token: TokenTree._create_tree(sentence, token, children_tokens),
                    tokens))
        except KeyError:
            trees = None

        return Tree(sentence[root.id], trees)

    def __init__(self, sentence):
        """
        Creates a new tree structure based on the provided Sentence object.

        Args:
            sentence: The constructed Sentence object to create a tree from.
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

        if root_token:
            root = TokenTree._create_tree(self.sentence, root_token,
                                          children_tokens)

        super().__init__(root_token, root.children)

    @property
    def sentence(self):
        """
        Provides the Sentence that this TokenTree represents.

        Returns:
            The wrapped Sentence.
        """
        return self._sentence
