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
