"""
Holds the Conllable interface, which is a marker interface to show that a class
is a Conll object, such as a treebank, sentence, or token, and therefore has a
conll method.
"""

class Conllable:
    """
    A Conllable mixin to indicate that the component can be converted into a
    CoNLL representation.
    """

    def conll(self):
        """
        Provides a conll representation of the component.

        Returns:
            A string conll representation of the base component.

        Raises:
            NotImplementedError: If the child class does not implement the
                method.
        """
        raise NotImplementedError("No implementation for conll")
