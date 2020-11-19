"""
The Conllable interface is a marker interface to show that a class is in the
Conll object domain, such as a treebank (Conll in this library), sentence, or
token, and therefore has a conll method.
"""

import abc


class Conllable(metaclass=abc.ABCMeta):
    """
    A Conllable mixin to indicate that the component can be converted into a
    CoNLL representation.
    """
    @abc.abstractmethod
    def conll(self) -> str:
        """
        Provides a conll representation of the component.

        Returns:
            A string conll representation of the base component.

        Raises:
            NotImplementedError: If the child class does not implement the
                method.
        """
        raise NotImplementedError("No implementation for conll")
