import pytest

from pyconll.conllu import conllu, fast_conllu


@pytest.fixture(params=[conllu, fast_conllu], ids=["conllu", "fast_conllu"])
def conllu_format(request):
    """Parameterize all tests over all CoNLL-U format providers."""
    return request.param
