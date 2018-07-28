import pytest

from pyconll.unit import Token
from tests.unit.util import assert_token_members


def test_construction():
    """
    Test the normal construction of a general token.
    """
    token_line = '7	vie	vie	NOUN	_	Gender=Fem|Number=Sing	4	nmod	_	SpaceAfter=No\n'
    token = Token(token_line)

    assert_token_members(token, '7', 'vie', 'vie', 'NOUN', None, {
        'Gender': set(('Fem', )),
        'Number': set(('Sing', ))
    }, '4', 'nmod', {}, {'SpaceAfter': set(('No', ))})


def test_construction_no_newline():
    """
    Test the construction of a token with no newline at the end of the line.
    """
    token_line = '7	vie	vie	NOUN	_	Gender=Fem|Number=Sing	4	nmod	_	_'
    token = Token(token_line)

    assert_token_members(token, '7', 'vie', 'vie', 'NOUN', None, {
        'Gender': set(('Fem', )),
        'Number': set(('Sing', ))
    }, '4', 'nmod', {}, {})


def test_only_form_and_lemma():
    """
    Test construction when token line only has a form and lemma.
    """
    token_line = '10.1	micro-pays	micro-pays	_	_	_	_	_	_	_\n'
    token = Token(token_line)

    assert_token_members(token, '10.1', 'micro-pays', 'micro-pays', None, None,
                         {}, None, None, {}, {})


def test_form_readonly():
    """
    Test that the word form for a Token is readonly.
    """
    token_line = '7	vie	vie	NOUN	_	Gender=Fem|Number=Sing	4	nmod	_	_'
    token = Token(token_line)

    with pytest.raises(AttributeError):
        token.form = 'vi'


def test_multiple_features_modify():
    """
    Test modification of features.
    """
    token_line = '28	une	un	DET	_	' \
        'Definite=Ind|Gender=Fem|Number=Sing|PronType=Art	30	det	_	_\n'
    token = Token(token_line)

    assert_token_members(
        token, '28', 'une', 'un', 'DET', None, {
            'Definite': set(('Ind', )),
            'Gender': set(('Fem', )),
            'Number': set(('Sing', )),
            'PronType': set(('Art', ))
        }, '30', 'det', {}, {})

    # Somehow this word is definite and indefinite!
    token.feats['Definite'].add('Def')

    assert_token_members(
        token, '28', 'une', 'un', 'DET', None, {
            'Definite': set(('Ind', 'Def')),
            'Gender': set(('Fem', )),
            'Number': set(('Sing', )),
            'PronType': set(('Art', ))
        }, '30', 'det', {}, {})


def test_deps_construction():
    """
    Test construction of a token when the deps field is present.
    """
    token_line = '1	They	they	PRON	PRP	Case=Nom|Number=Plur	2	nsubj	2:nsubj|4:nsubj	_\n'
    token = Token(token_line)

    assert_token_members(token, '1', 'They', 'they', 'PRON', 'PRP', {
        'Case': set(('Nom', )),
        'Number': set(('Plur', ))
    }, '2', 'nsubj', {
        '2': 'nsubj',
        '4': 'nsubj'
    }, {})


def test_multiword_construction():
    """
    Test the creation of a token that is a multiword token line.
    """
    token_line = '8-9	du	_	_	_	_	_	_	_	_'
    token = Token(token_line)

    assert_token_members(token, '8-9', 'du', None, None, None, {}, None, None,
                         {}, {})
    assert token.is_multiword()


def test_to_string():
    """
    Test if a token's string representation is accurate.
    """
    token_line =  '26	surmonté	surmonter	VERB	_	' \
        'Gender=Masc|Number=Sing|Tense=Past|VerbForm=Part	22	acl	_	_'
    token = Token(token_line)

    assert token.conll() == token_line


def test_modify_unit_field_to_string():
    """
    Test a token's string representation after changing one of it's fields.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender=Masc|Number=Sing	' \
        '30	nmod	_	SpaceAfter=No'
    token = Token(token_line)

    token.lemma = 'pain'

    new_token_line = '33	cintre	pain	NOUN	_	' \
        'Gender=Masc|Number=Sing	30	nmod	_	SpaceAfter=No'

    assert token.conll() == new_token_line


def test_modify_dict_field_to_string():
    """
    Test a token's string representation after adding a feature.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender=Masc|Number=Sing	' \
        '30	nmod	_	SpaceAfter=No'
    token = Token(token_line)

    token.feats['Gender'].add('Fem')

    new_token_line = '33	cintre	cintre	NOUN	_	' \
        'Gender=Fem,Masc|Number=Sing	30	nmod	_	SpaceAfter=No'

    assert token.conll() == new_token_line


def test_remove_feature_to_string():
    """
    Test a token's string representation after removing a feature completely.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender=Masc|Number=Sing	' \
        '30	nmod	_	SpaceAfter=No'
    token = Token(token_line)

    del token.feats['Gender']

    new_token_line = '33	cintre	cintre	NOUN	_	' \
        'Number=Sing	30	nmod	_	SpaceAfter=No'

    assert token.conll() == new_token_line


def test_underscore_construction():
    """
    Test construction of token without empty assumption and no form or lemma.
    """
    token_line = '33	_	_	PUN	_	_	30	nmod	_	SpaceAfter=No'
    token = Token(token_line, empty=False)

    assert_token_members(token, '33', '_', '_', 'PUN', None, {}, '30', 'nmod',
                         {}, {'SpaceAfter': set(('No', ))})


def test_empty_form_present_lemma():
    """
    Test construction of token without empty assumption and no form but a present lemma.
    """
    token_line = '33	hate	_	VERB	_	_	30	nmod	_	SpaceAfter=No'
    token = Token(token_line, empty=False)

    assert_token_members(token, '33', 'hate', None, 'VERB', None, {}, '30',
                         'nmod', {}, {'SpaceAfter': set(('No', ))})


def test_empty_lemma_present_form():
    """
    Test construction of token without empty assumption and no lemma but a present form.
    """
    token_line = '33	_	hate	VERB	_	_	30	nmod	_	SpaceAfter=No'
    token = Token(token_line, empty=False)

    assert_token_members(token, '33', None, 'hate', 'VERB', None, {}, '30',
                         'nmod', {}, {'SpaceAfter': set(('No', ))})


def test_improper_source():
    """
    Test that when an input without 10 delimited columns raises a ValueError.
    """
    token_line = '33	hate	_	VERB	_	_	30	nmod	_'

    with pytest.raises(ValueError):
        token = Token(token_line)


def test_misc_parsing():
    """
    Test that a misc field is properly parsed in all of its cases.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender=Masc|Number=Sing	' \
        '30	nmod	_	SpaceAfter=No|French|Independent=P,Q'
    token = Token(token_line)

    assert 'SpaceAfter' in token.misc
    assert 'French' in token.misc
    assert 'Independent' in token.misc

    assert token.misc['SpaceAfter'] == set(('No', ))
    assert token.misc['French'] is None
    assert token.misc['Independent'] == set(('P', 'Q'))


def test_deps_parsing():
    """
    Test that the deps field is properly parsed.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender=Masc|Number=Sing	' \
        '30	nmod	2:nsubj|4:nmod	SpaceAfter=No'
    token = Token(token_line)

    assert token.deps['2'] == 'nsubj'
    assert token.deps['4'] == 'nmod'
    assert token.conll() == token_line


def test_invalid_token():
    """
    Test that a token is identified as invalid.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender=Masc|Number=Sing	'

    with pytest.raises(ValueError):
        token = Token(token_line)


def test_invalid_token_feats():
    """
    Test that the features field must have an attribute value form.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender|Number=Sing	' \
        '30	nmod	_	SpaceAfter=No|French|Independent=P,Q'

    with pytest.raises(ValueError):
        token = Token(token_line)


def test_invalid_token_deps():
    """
    Test that there is no singleton parsing in the misc field.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender=Fem|Number=Sing	' \
        '30	nmod	_	SpaceAfter=No'
    token = Token(token_line)

    assert token.misc['SpaceAfter'] == set(('No', ))


def test_enhanced_deps_parsing():
    """
    Test that the enhanced deps field is parsed properly.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender=Fem|Number=Sing	' \
        '30	nmod	2:nsubj,noun|4:root	SpaceAfter=No'
    token = Token(token_line)

    assert token.deps['2'] == 'nsubj,noun'
    assert token.deps['4'] == 'root'


def test_enhanced_deps_parsing_invalid():
    """
    Test that an error is thrown when the enhanced deps is invalid.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender=Fem|Number=Sing	' \
        '30	nmod	2:nsubj|4	SpaceAfter=No'
    with pytest.raises(ValueError):
        token = Token(token_line)


def test_misc_parsing_output():
    """
    Test that the misc field is properly output in CoNLL-U format.
    """
    token_line = '33	cintre	cintre	NOUN	_	Gender=Fem|Number=Sing	' \
        '30	nmod	2:nsubj|4:root	SpaceAfter=No'
    token = Token(token_line)

    token.misc['Independent'] = None
    token.misc['SpaceAfter'].add('Yes')

    token.misc['OtherTest'] = set()
    token.misc['OtherTest'].add('X')
    token.misc['OtherTest'].add('Z')
    token.misc['OtherTest'].add('Y')

    expected_output = '33	cintre	cintre	NOUN	_	Gender=Fem|Number=Sing	' \
        '30	nmod	2:nsubj|4:root	Independent|OtherTest=X,Y,Z|SpaceAfter=No,Yes'
    assert expected_output == token.conll()
