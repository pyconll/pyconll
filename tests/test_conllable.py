import pytest

from pyconll.conllable import Conllable


def test_conllable_throws_exception():
    """
    Test that the base Conllable implementation cannot be instantiated.
    """

    with pytest.raises(TypeError):
        c = Conllable()
