import pytest

from pyconllu.unit import Sentence
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

    assert sentence.meta('sent_id') == 'fr-ud-dev_00003'
    assert sentence.meta('newdoc id') == 'test id'
    assert sentence.meta('text') == 'Mais comment faire ?'
    assert sentence.meta('text_en') == 'But how is it done ?'
    assert sentence.meta('translit') == 'tat yathānuśrūyate.'


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

    assert sentence.meta('sent_id') == 'fr-ud-dev_00003'
    assert sentence.meta('newdoc') is True
    assert sentence.meta('text') == 'Mais comment faire ?'
    assert sentence.meta('text_en') == 'But how is it done ?'
    assert sentence.meta('translit') == 'tat yathānuśrūyate.'


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
    assert sentence.meta('sent_id') == 'fr-ud-train_00123'


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

    assert sentence.conllu() == source


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

    assert sentence.conllu() == output
