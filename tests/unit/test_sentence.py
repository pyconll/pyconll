import pytest

from pyconll.unit import Sentence
from tests.unit.util import assert_token_members


def test_simple_sentence_construction():
    """
    Test the construction of a simple sentence.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# text = Mais comment faire ?\n'
              '1	Mais	mais	CCONJ	_	_	3	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = Sentence(source)

    assert sentence.id == 'fr-ud-dev_00003'
    assert sentence.text == 'Mais comment faire ?'
    assert len(sentence) == 4

    assert_token_members(sentence['1'], '1', 'Mais', 'mais', 'CCONJ', None, {},
                         '3', 'cc', {}, {})
    assert_token_members(sentence['2'], '2', 'comment', 'comment', 'ADV', None,
                         {}, '3', 'advmod', {}, {})
    assert_token_members(sentence['3'], '3', 'faire', 'faire', 'VERB', None,
                         {'VerbForm': set(('Inf', ))}, '0', 'root', {}, {})
    assert_token_members(sentence['4'], '4', '?', '?', 'PUNCT', None, {}, '3',
                         'punct', {}, {})


def test_cannot_assign_tokens():
    """
    Test Sentence tokens cannot be assigned by id.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# text = Mais comment faire ?\n'
              '1	Mais	mais	CCONJ	_	_	3	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = Sentence(source)

    with pytest.raises(TypeError):
        sentence['1'] = sentence['2']


def test_metadata_parsing():
    """
    Test if the sentence can accurately parse all metadata in the comments.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# newdoc id = test id\n'
              '# text = Mais comment faire ?\n'
              '# text_en = But how is it done ?\n'
              '# translit = tat yathānuśrūyate.\n'
              '1	Mais	mais	CCONJ	_	_	3	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = Sentence(source)

    assert sentence.meta_value('sent_id') == 'fr-ud-dev_00003'
    assert sentence.meta_value('newdoc id') == 'test id'
    assert sentence.meta_value('text') == 'Mais comment faire ?'
    assert sentence.meta_value('text_en') == 'But how is it done ?'
    assert sentence.meta_value('translit') == 'tat yathānuśrūyate.'

    assert sentence.meta_present('text') is True
    assert sentence.meta_present('translit') is True
    assert sentence.meta_present('fake') is False


def test_singleton_parsing():
    """
    Test if the sentence can accurately parse all metadata in the comments.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# newdoc\n'
              '# text = Mais comment faire ?\n'
              '# text_en = But how is it done ?\n'
              '# translit = tat yathānuśrūyate.\n'
              '1	Mais	mais	CCONJ	_	_	3	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = Sentence(source)

    assert sentence.meta_value('sent_id') == 'fr-ud-dev_00003'
    assert sentence.meta_present('newdoc') is True
    assert sentence.meta_value('text') == 'Mais comment faire ?'
    assert sentence.meta_value('text_en') == 'But how is it done ?'
    assert sentence.meta_value('translit') == 'tat yathānuśrūyate.'


def test_metadata_error():
    """
    Test if the proper error is seen when asking for the value of a nonexisting
    comment.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# newdoc\n'
              '# text = Mais comment faire ?\n'
              '# text_en = But how is it done ?\n'
              '# translit = tat yathānuśrūyate.\n'
              '1	Mais	mais	CCONJ	_	_	3	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = Sentence(source)

    with pytest.raises(KeyError):
        sentence.meta_value('newpar')


def test_id_updating():
    """
    Test updating the sentence id.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# newdoc id = test id\n'
              '# text = Mais comment faire ?\n'
              '# text_en = But how is it done ?\n'
              '# translit = tat yathānuśrūyate.\n'
              '1	Mais	mais	CCONJ	_	_	3	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = Sentence(source)

    sentence.id = 'fr-ud-train_00123'
    assert sentence.meta_value('sent_id') == 'fr-ud-train_00123'


def test_iter():
    """
    Test that the sentence can be properly iterated over.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# newdoc id = test id\n'
              '# text = Mais comment faire ?\n'
              '# text_en = But how is it done ?\n'
              '# translit = tat yathānuśrūyate.\n'
              '1	Mais	mais	CCONJ	_	_	3	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = Sentence(source)

    expected_ids = ['1', '2', '3', '4']
    expected_forms = ['Mais', 'comment', 'faire', '?']
    actual_ids = [token.id for token in sentence]
    actual_forms = [token.form for token in sentence]

    assert expected_ids == actual_ids
    assert expected_forms == actual_forms


def test_str_indexing():
    """
    Test indexing by token id (string).
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')
    sentence = Sentence(source)

    test_token = sentence['8']
    assert_token_members(test_token, '8', 'contenu', 'contenu', 'NOUN', None, {
        'Gender': set(('Masc', )),
        'Number': set(('Sing', ))
    }, '9', 'nsubj', {}, {})


def test_int_indexing():
    """
    Test indexing by the integer position in the sentence (int).
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')
    sentence = Sentence(source)

    test_token = sentence[7]
    assert_token_members(test_token, '8', 'contenu', 'contenu', 'NOUN', None, {
        'Gender': set(('Masc', )),
        'Number': set(('Sing', ))
    }, '9', 'nsubj', {}, {})


def test_int_slice_indexing():
    """
    Test slicing with integer over tokens.
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')
    sentence = Sentence(source)

    test_tokens = sentence[7:10]
    assert_token_members(test_tokens[0], '8', 'contenu', 'contenu', 'NOUN',
                         None, {
                             'Gender': set(('Masc', )),
                             'Number': set(('Sing', ))
                         }, '9', 'nsubj', {}, {})
    assert_token_members(
        test_tokens[1], '9', 'diffère', 'différer', 'VERB', None, {
            'Mood': set(('Ind', )),
            'Number': set(('Sing', )),
            'Person': set(('3', )),
            'Tense': set(('Pres', )),
            'VerbForm': set(('Fin', ))
        }, '3', 'conj', {}, {})
    assert_token_members(test_tokens[2], '10', 'donc', 'donc', 'ADV', None, {},
                         '9', 'advmod', {}, {})


def test_str_slice_indexing():
    """
    Test slicing with strings over tokens.
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')
    sentence = Sentence(source)

    test_tokens = sentence['8':'11']
    assert_token_members(test_tokens[0], '8', 'contenu', 'contenu', 'NOUN',
                         None, {
                             'Gender': set(('Masc', )),
                             'Number': set(('Sing', ))
                         }, '9', 'nsubj', {}, {})
    assert_token_members(
        test_tokens[1], '9', 'diffère', 'différer', 'VERB', None, {
            'Mood': set(('Ind', )),
            'Number': set(('Sing', )),
            'Person': set(('3', )),
            'Tense': set(('Pres', )),
            'VerbForm': set(('Fin', ))
        }, '3', 'conj', {}, {})
    assert_token_members(test_tokens[2], '10', 'donc', 'donc', 'ADV', None, {},
                         '9', 'advmod', {}, {})


def test_len_basic():
    """
    Test if the length is appropriate for a normal sentence.
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')
    sentence = Sentence(source)

    assert len(sentence) == 14


def test_len_empty():
    """
    Test if an empty sentence is properly parsed.
    """
    source = ''
    sentence = Sentence(source)

    assert len(sentence) == 0


def test_text_readonly():
    """
    Test that the text comment of a Sentence is read properly and is readonly.
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')
    sentence = Sentence(source)

    with pytest.raises(AttributeError):
        sentence.text = 'error causing text'

    assert sentence.text == 'Les études durent six ans mais leur contenu diffère donc selon les Facultés.'


def test_output():
    """
    Test if the sentence output is propertly produced.
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')
    sentence = Sentence(source)

    assert sentence.conll() == source


def test_modified_output():
    """
    Test if the sentence is properly outputted after changing the annotation.
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')
    sentence = Sentence(source)

    sentence.id = 'fr-ud-dev_00231'
    sentence['13'].lemma = 'facultés'
    sentence['13'].upos = 'NOUN'

    sentence['13'].feats['Number'] = set()
    sentence['13'].feats['Number'].add('Fem')

    output = (
        '# sent_id = fr-ud-dev_00231\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	facultés	NOUN	_	Number=Fem	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')

    assert sentence.conll() == output


def test_token_line_numbers():
    """
    Test that the lines for tokens are correct.
    """
    sent_start = 14
    sent_end = 29
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')
    sentence = Sentence(
        source, _start_line_number=sent_start, _end_line_number=sent_end)

    assert sentence['1'].line_number == 16
    assert sentence['7'].line_number == 22


def test_change_comments():
    """
    Test that comment values (other than text or id) can be changed through the
    meta api.
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')

    expected = (
        '# newpar id = xyz-1\n'
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')

    sentence = Sentence(source)
    sentence.set_meta('newpar id', 'xyz-1')

    assert sentence.conll() == expected


def test_add_comments():
    """
    Test that comment values (other than text or id) can be added through the
    meta api.
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')

    expected = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '# x-coord = 2\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')

    sentence = Sentence(source)
    sentence.set_meta('x-coord', '2')

    assert sentence.conll() == expected


def test_singleton_comment():
    """
    Test that a singleton comment is properly output.
    """
    source = (
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')

    expected = (
        '# foreign\n'
        '# sent_id = fr-ud-dev_00002\n'
        '# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n'
        '1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n'
        '2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n'
        '3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n'
        '4	six	six	NUM	_	_	5	nummod	_	_\n'
        '5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n'
        '6	mais	mais	CCONJ	_	_	9	cc	_	_\n'
        '7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n'
        '8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n'
        '9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n'
        '10	donc	donc	ADV	_	_	9	advmod	_	_\n'
        '11	selon	selon	ADP	_	_	13	case	_	_\n'
        '12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n'
        '13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n'
        '14	.	.	PUNCT	_	_	3	punct	_	_')

    sentence = Sentence(source)
    sentence.set_meta('foreign')

    assert sentence.conll() == expected
