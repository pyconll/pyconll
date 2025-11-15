import pytest

from pyconll.conllu import conllu, compact_conllu


@pytest.fixture(params=[conllu, compact_conllu], ids=["conllu", "compact_conllu"])
def conllu_format(request):
    """Parameterize all tests over all CoNLL-U format providers."""
    return request.param
