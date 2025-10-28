import pytest

from pyconll.conllable import Conllable


def test_conllable_throws_exception():
    """
    Test that the base Conllable implementation cannot be instantiated.
    """

    with pytest.raises(TypeError):
        c = Conllable()


def test_conllable_base_not_implemented():
    """
    Test that the Conllable base class implementation cannot be used.
    """

    class ConllableObj(Conllable):
        def conll(self) -> str:
            return super().conll()

    with pytest.raises(RuntimeError):
        c = ConllableObj()
        c.conll()
