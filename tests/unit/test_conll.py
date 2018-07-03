import os

from pyconll.unit import Conll
from pyconll.unit import Sentence
from tests.util import fixture_location


def test_creation():
    """
    Test the basic creation of a Conll object.
    """
    with open(fixture_location('basic.conll')) as f:
        conll = Conll(f)

    assert len(conll) == 4

    assert len(conll[0]) == 10
    assert conll[0].id == 'fr-ud-dev_00001'

    assert len(conll[1]) == 14
    assert conll[1].id == 'fr-ud-dev_00002'

    assert len(conll[2]) == 9
    assert conll[2].id == 'fr-ud-dev_00003'

    assert len(conll[3]) == 52
    assert conll[3].id == 'fr-ud-dev_00004'


def test_no_ending_newline():
    """
    Test correct creation when the ending of the file ends in no newline.
    """
    with open(fixture_location('no_newline.conll')) as f:
        conll = Conll(f)

    assert len(conll) == 3

    assert len(conll[0]) == 10
    assert conll[0].id == 'fr-ud-dev_00001'

    assert len(conll[1]) == 14
    assert conll[1].id == 'fr-ud-dev_00002'

    assert len(conll[2]) == 9
    assert conll[2].id == 'fr-ud-dev_00003'


def test_many_newlines():
    """
    Test correct Conll parsing when there are too many newlines.
    """
    with open(fixture_location('many_newlines.conll')) as f:
        conll = Conll(f)

    assert len(conll) == 4

    assert len(conll[0]) == 10
    assert conll[0].id == 'fr-ud-dev_00001'

    assert len(conll[1]) == 14
    assert conll[1].id == 'fr-ud-dev_00002'

    assert len(conll[2]) == 9
    assert conll[2].id == 'fr-ud-dev_00003'

    assert len(conll[3]) == 52
    assert conll[3].id == 'fr-ud-dev_00004'


def test_numeric_indexing():
    """
    Test the ability to index sentences through their numeric position.
    """
    with open(fixture_location('basic.conll')) as f:
        conll = Conll(f)

    assert len(conll[0]) == 10
    assert conll[0].id == 'fr-ud-dev_00001'


def test_slice_indexing():
    """
    Test the ability to slice up a Conll object and its result.
    """
    with open(fixture_location('long.conll')) as f:
        conll = Conll(f)

    every_3 = conll[1:7:3]

    assert len(every_3) == 2
    assert every_3[0].id == 'fr-ud-test_00002'
    assert len(every_3[1]) == 38

    every_2 = conll[1:6:2]
    assert len(every_2) == 3


def test_string_output():
    """
    Test that the strings are properly created.
    """
    with open(fixture_location('basic.conll')) as f:
        contents = f.read()
        f.seek(0)
        conll = Conll(f)

    assert contents == conll.conll()


def test_writing_output():
    """
    Test that CoNLL files are properly created.
    """
    with open(fixture_location('basic.conll')) as f:
        contents_basic = f.read()
        f.seek(0)
        conll = Conll(f)

    output_loc = fixture_location('output.conll')
    with open(output_loc, 'w') as f:
        conll.write(f)

    with open(output_loc) as f:
        contents_write = f.read()
    os.remove(fixture_location('output.conll'))

    assert contents_basic == contents_write


def test_append():
    """
    Test that a sentence can be properly added to a Conll object.
    """
    with open(fixture_location('basic.conll')) as f:
        conll = Conll(f)
    orig_length = len(conll)

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

    conll.append(sentence)

    assert len(conll) == orig_length + 1
    assert conll[-1].id == 'fr-ud-dev_00002'
    assert len(conll[-1]) == 14


def test_insert():
    """
    Test that a sentence can be inserted to a Conll object.
    """
    with open(fixture_location('basic.conll')) as f:
        conll = Conll(f)
    orig_length = len(conll)

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

    conll.insert(2, sentence)

    assert len(conll) == orig_length + 1
    assert conll[2].id == 'fr-ud-dev_00002'
    assert len(conll[2]) == 14


def test_contains_true():
    """
    Test that a Conll object can test for membership presence properly.
    """
    with open(fixture_location('basic.conll')) as f:
        conll = Conll(f)

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
    conll.append(sentence)

    assert sentence in conll

    sentence['1'].pos = 'NOUN'

    assert sentence in conll


def test_contains_false():
    """
    Test that a Conll object can test for membership presence.
    """
    with open(fixture_location('basic.conll')) as f:
        conll = Conll(f)

    source = (
        '# sent_id = fr-ud-dev_00002'
        '# text = Thionville et Congerville furent créée en 1793 avec leur nom actuel et fusionnèrent en 1973.\n'
        '1	Thionville	Thionville	PROPN	_	_	5	nsubj:pass	_	_\n'
        '2	et	et	CCONJ	_	_	3	cc	_	_\n'
        '3	Congerville	Congerville	PROPN	_	_	1	conj	_	_\n'
        '4	furent	être	AUX	_	Mood=Ind|Number=Plur|Person=3|Tense=Past|VerbForm=Fin	5	aux:pass	_	_\n'
        '5	créée	créer	VERB	_	Gender=Fem|Number=Sing|Tense=Past|VerbForm=Part	0	root	_	_\n'
        '6	en	en	ADP	_	_	7	case	_	_\n'
        '7	1793	1793	NUM	_	_	5	obl	_	_\n'
        '8	avec	avec	ADP	_	_	10	case	_	_\n'
        '9	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	10	det	_	_\n'
        '10	nom	nom	NOUN	_	Gender=Masc|Number=Sing	5	obl:mod	_	_\n'
        '11	actuel	actuel	ADJ	_	Gender=Masc|Number=Sing	10	amod	_	_\n'
        '12	et	et	CCONJ	_	_	13	cc	_	_\n'
        '13	fusionnèrent	fusionner	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Past|VerbForm=Fin	5	conj	_	_\n'
        '14	en	en	ADP	_	_	15	case	_	_\n'
        '15	1973	1973	NUM	_	_	13	obl	_	SpaceAfter=No\n'
        '16	.	.	PUNCT	_	_	5	punct	_	_\n')
    sentence = Sentence(source)

    assert sentence not in conll


def test_contains_non_existent_id():
    """
    Test that contains properly executes when the sentence id is unknown.
    """
    with open(fixture_location('basic.conll')) as f:
        conll = Conll(f)

    source = (
        '# sent_id = fr-ud-dev_00037'
        '# text = Thionville et Congerville furent créée en 1793 avec leur nom actuel et fusionnèrent en 1973.\n'
        '1	Thionville	Thionville	PROPN	_	_	5	nsubj:pass	_	_\n'
        '2	et	et	CCONJ	_	_	3	cc	_	_\n'
        '3	Congerville	Congerville	PROPN	_	_	1	conj	_	_\n'
        '4	furent	être	AUX	_	Mood=Ind|Number=Plur|Person=3|Tense=Past|VerbForm=Fin	5	aux:pass	_	_\n'
        '5	créée	créer	VERB	_	Gender=Fem|Number=Sing|Tense=Past|VerbForm=Part	0	root	_	_\n'
        '6	en	en	ADP	_	_	7	case	_	_\n'
        '7	1793	1793	NUM	_	_	5	obl	_	_\n'
        '8	avec	avec	ADP	_	_	10	case	_	_\n'
        '9	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	10	det	_	_\n'
        '10	nom	nom	NOUN	_	Gender=Masc|Number=Sing	5	obl:mod	_	_\n'
        '11	actuel	actuel	ADJ	_	Gender=Masc|Number=Sing	10	amod	_	_\n'
        '12	et	et	CCONJ	_	_	13	cc	_	_\n'
        '13	fusionnèrent	fusionner	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Past|VerbForm=Fin	5	conj	_	_\n'
        '14	en	en	ADP	_	_	15	case	_	_\n'
        '15	1973	1973	NUM	_	_	13	obl	_	SpaceAfter=No\n'
        '16	.	.	PUNCT	_	_	5	punct	_	_\n')
    sentence = Sentence(source)

    assert sentence not in conll


def test_sentence_line_numbers():
    """
    Test that the CoNLL files properly associate line numbers.
    """
    sentence_bounds = [(1, 12), (14, 29), (31, 41), (43, 96)]

    with open(fixture_location('basic.conll')) as f:
        c = Conll(f)

    for i, sent in enumerate(c):
        cur_bounds = sentence_bounds[i]
        assert sent.start_line_number == cur_bounds[0]
        assert sent.end_line_number == cur_bounds[1]


def test_sentence_line_numbers_extra_newlines():
    """
    Test that the CoNLL files properly read in the sentence lines when there
    are extra newlines.
    """
    sentence_bounds = [(3, 14), (16, 31), (34, 44), (46, 99)]

    with open(fixture_location('many_newlines.conll')) as f:
        c = Conll(f)

    for i, sent in enumerate(c):
        cur_bounds = sentence_bounds[i]
        assert sent.start_line_number == cur_bounds[0]
        assert sent.end_line_number == cur_bounds[1]


def test_par_and_doc_id_basic():
    """
    Test that the paragraph and document ids are properly associated with the
    Sentences.
    """
    with open(fixture_location('par_doc_ids_basic.conll')) as f:
        c = Conll(f)

    expected_doc_ids = ['2', '2', '1', '1']
    actual_doc_ids = [s.doc_id for s in c]

    assert expected_doc_ids == actual_doc_ids


def test_par_and_doc_id_long():
    """
    Test that the paragraph and document ids are properly associated with the
    Sentences.
    """
    with open(fixture_location('par_doc_ids_long.conll')) as f:
        c = Conll(f)

    expected_doc_ids = [
        None, None, 'abc-1', 'abc-1', 'xyz-2', 'xyz-2', 'xyz-2', None, None
    ]
    actual_doc_ids = [s.doc_id for s in c]

    expected_par_ids = [None, None, None, '70', '70', None, '71', '71', '71']
    actual_par_ids = [s.par_id for s in c]

    assert expected_doc_ids == actual_doc_ids
    assert expected_par_ids == actual_par_ids


def test_setitem():
    """
    Test that Sentences are properly assigned when using setitem.
    """
    with open(fixture_location('basic.conll')) as f:
        c = Conll(f)

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

    c[1] = sentence
    assert c[1].conll() == source
    assert c[1].id == 'fr-ud-dev_00002'


def test_delitem_single_int():
    """
    Test that Sentences keyed by index are properly deleted from Conll objects.
    """
    with open(fixture_location('basic.conll')) as f:
        c = Conll(f)

    del c[2]
    assert len(c) == 3
    assert c[2].id == 'fr-ud-dev_00004'


def test_delitem_slice_int():
    """
    Test that Sentences can be deleted through slices with integer boundaries.
    """
    with open(fixture_location('long.conll')) as f:
        c = Conll(f)

    del c[3:8:2]
    assert len(c) == 6

    expected_ids = ['fr-ud-test_0000{}'.format(i + 1) for i in range(9)]
    del expected_ids[3:8:2]
    actual_ids = [sent.id for sent in c]
    assert actual_ids == expected_ids


def test_delitem_contains():
    """
    Test that the contains method still works after deletion.
    """
    with open(fixture_location('long.conll')) as f:
        c = Conll(f)

    sent = c[1]

    assert sent in c
    del c[1]
    assert sent not in c


def test_insert_contains():
    """
    Test that contains still works after inserting an Sentence.
    """
    with open(fixture_location('long.conll')) as f:
        c = Conll(f)

    sent = c[6]
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
    new_sent = Sentence(source)
    other_sent = Sentence(source)
    other_sent.id = 'xyz'

    c.insert(3, new_sent)

    assert new_sent in c
    assert sent in c
    assert other_sent not in c


def test_append_contains():
    """
    Test that contains still works after appending an Sentence.
    """
    with open(fixture_location('long.conll')) as f:
        c = Conll(f)

    sent = c[6]
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
    new_sent = Sentence(source)
    other_sent = Sentence(source)
    other_sent.id = 'xyz'

    c.append(new_sent)

    assert new_sent in c
    assert sent in c
    assert other_sent not in c
