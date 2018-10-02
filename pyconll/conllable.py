class Conllable:
    """
    A Conllable mixin to indicate that the component can be converted into a
    CoNLL representation.
    """
    def conll():
        raise NotImplementedError("No implementation for conll")
