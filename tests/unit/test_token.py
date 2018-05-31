from pyconllu.unit import Token

def _test_token_members(token, id, form, lemma, upos, xpos, feats, head, deprel,
    deps, misc):
    # TODO: This uses equality for None comparison, is it worth doing differently?
    assert token.id == id
    assert token.form == form
    assert token.lemma == lemma
    assert token.upos == upos
    assert token.xpos == xpos
    assert token.feats == feats
    assert token.head == head
    assert token.deprel == deprel
    assert token.deps == deps
    assert token.misc == misc

def test_token_construction():
    """
    Test the normal construction of a general token.
    """
    token_line = '7	vie	vie	NOUN	_	Gender=Fem|Number=Sing	4	nmod	_	_\n'
    token = Token(token_line)

    _test_token_members(token, '7', 'vie', 'vie', 'NOUN', None,
        { 'Gender': set(('Fem',)), 'Number': set(('Sing',)) },
        '4', 'nmod', {}, [])

def test_token_construction_no_newline():
    """
    Test the construction of a token with no newline at the end of the line.
    """
    token_line = '7	vie	vie	NOUN	_	Gender=Fem|Number=Sing	4	nmod	_	_'
    token = Token(token_line)

    _test_token_members(token, '7', 'vie', 'vie', 'NOUN', None,
        { 'Gender': set(('Fem',)), 'Number': set(('Sing',)) },
        '4', 'nmod', {}, [])


def test_token_only_form_and_lemma():
    """
    Test construction when token line only has a form and lemma.
    """
    token_line = '10.1	micro-pays	micro-pays	_	_	_	_	_	_	_\n'
    token = Token(token_line)

    _test_token_members(token, '10.1', 'micro-pays', 'micro-pays', None, None,
        {}, None, None, {}, [])

def test_token_multiple_features_modify():
    """
    Test modification of features.
    """
    token_line = '28	une	un	DET	_	' \
        'Definite=Ind|Gender=Fem|Number=Sing|PronType=Art	30	det	_	_\n'
    token = Token(token_line)

    _test_token_members(token, '28', 'une', 'un', 'DET', None,
        { 'Definite': set(('Ind',)),
          'Gender': set(('Fem',)),
          'Number': set(('Sing',)),
          'PronType': set(('Art',))
        },
        '30', 'det', {}, [])

    # Somehow this word is definite and indefinite.
    token.feats['Definite'].add('Def')

    _test_token_members(token, '28', 'une', 'un', 'DET', None,
        { 'Definite': set(('Ind', 'Def')),
          'Gender': set(('Fem',)),
          'Number': set(('Sing',)),
          'PronType': set(('Art',))
        },
        '30', 'det', {}, [])
