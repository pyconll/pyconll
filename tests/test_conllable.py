import pytest

from pyconll.conllable import Conllable


def test_conllable_throws_exception():
    """
    Test that the base Conllable implementation throws an exception.
    """
    c = Conllable()

    with pytest.raises(NotImplementedError):
        c.conll()
