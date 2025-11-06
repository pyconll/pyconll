import pytest

from pyconll.exception import FormatError
from tests.unit.util import assert_token_members, parse_sentence


def test_simple_sentence_construction():
    """
    Test the construction of a simple sentence.
    """
    source = (
        "# sent_id = fr-ud-dev_00003\n"
        "# text = Mais comment faire ?\n"
        "1	Mais	mais	CCONJ	_	_	3	cc	_	_\n"
        "2	comment	comment	ADV	_	_	3	advmod	_	_\n"
        "3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n"
        "4	?	?	PUNCT	_	_	3	punct	_	_\n"
    )
    sentence = parse_sentence(source)

    assert sentence.meta["sent_id"] == "fr-ud-dev_00003"
    assert sentence.meta["text"] == "Mais comment faire ?"
    assert len(sentence.tokens) == 4

    assert_token_members(
        sentence.tokens[0], "1", "Mais", "mais", "CCONJ", None, {}, "3", "cc", {}, {}
    )
    assert_token_members(
        sentence.tokens[1], "2", "comment", "comment", "ADV", None, {}, "3", "advmod", {}, {}
    )
    assert_token_members(
        sentence.tokens[2],
        "3",
        "faire",
        "faire",
        "VERB",
        None,
        {"VerbForm": set(("Inf",))},
        "0",
        "root",
        {},
        {},
    )
    assert_token_members(sentence.tokens[3], "4", "?", "?", "PUNCT", None, {}, "3", "punct", {}, {})


def test_metadata_parsing():
    """
    Test if the sentence can accurately parse all metadata in the comments.
    """
    source = (
        "# sent_id = fr-ud-dev_00003\n"
        "# newdoc id = test id\n"
        "# text = Mais comment faire ?\n"
        "# text_en = But how is it done ?\n"
        "# translit = tat yathānuśrūyate.\n"
        "1	Mais	mais	CCONJ	_	_	3	cc	_	_\n"
        "2	comment	comment	ADV	_	_	3	advmod	_	_\n"
        "3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n"
        "4	?	?	PUNCT	_	_	3	punct	_	_\n"
    )
    sentence = parse_sentence(source)

    assert sentence.meta["sent_id"] == "fr-ud-dev_00003"
    assert sentence.meta["newdoc id"] == "test id"
    assert sentence.meta["text"] == "Mais comment faire ?"
    assert sentence.meta["text_en"] == "But how is it done ?"
    assert sentence.meta["translit"] == "tat yathānuśrūyate."

    assert "text" in sentence.meta
    assert "translit" in sentence.meta
    assert "fake" not in sentence.meta


def test_singleton_parsing():
    """
    Test if the sentence can accurately parse all metadata in the comments.
    """
    source = (
        "# sent_id = fr-ud-dev_00003\n"
        "# newdoc\n"
        "# text = Mais comment faire ?\n"
        "# text_en = But how is it done ?\n"
        "# translit = tat yathānuśrūyate.\n"
        "1	Mais	mais	CCONJ	_	_	3	cc	_	_\n"
        "2	comment	comment	ADV	_	_	3	advmod	_	_\n"
        "3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n"
        "4	?	?	PUNCT	_	_	3	punct	_	_\n"
    )
    sentence = parse_sentence(source)

    assert sentence.meta["sent_id"] == "fr-ud-dev_00003"
    assert "newdoc" in sentence.meta
    assert sentence.meta["text"] == "Mais comment faire ?"
    assert sentence.meta["text_en"] == "But how is it done ?"
    assert sentence.meta["translit"] == "tat yathānuśrūyate."


def test_metadata_error():
    """
    Test if the proper error is seen when asking for the value of a nonexisting
    comment.
    """
    source = (
        "# sent_id = fr-ud-dev_00003\n"
        "# newdoc\n"
        "# text = Mais comment faire ?\n"
        "# text_en = But how is it done ?\n"
        "# translit = tat yathānuśrūyate.\n"
        "1	Mais	mais	CCONJ	_	_	3	cc	_	_\n"
        "2	comment	comment	ADV	_	_	3	advmod	_	_\n"
        "3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n"
        "4	?	?	PUNCT	_	_	3	punct	_	_\n"
    )
    sentence = parse_sentence(source)

    with pytest.raises(KeyError):
        sentence.meta["newpar"]


def test_iter():
    """
    Test that the sentence can be properly iterated over.
    """
    source = (
        "# sent_id = fr-ud-dev_00003\n"
        "# newdoc id = test id\n"
        "# text = Mais comment faire ?\n"
        "# text_en = But how is it done ?\n"
        "# translit = tat yathānuśrūyate.\n"
        "1	Mais	mais	CCONJ	_	_	3	cc	_	_\n"
        "2	comment	comment	ADV	_	_	3	advmod	_	_\n"
        "3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n"
        "4	?	?	PUNCT	_	_	3	punct	_	_\n"
    )
    sentence = parse_sentence(source)

    expected_ids = ["1", "2", "3", "4"]
    expected_forms = ["Mais", "comment", "faire", "?"]
    actual_ids = [token.id for token in sentence.tokens]
    actual_forms = [token.form for token in sentence.tokens]

    assert expected_ids == actual_ids
    assert expected_forms == actual_forms


def test_len_basic():
    """
    Test if the length is appropriate for a normal sentence.
    """
    source = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )
    sentence = parse_sentence(source)

    assert len(sentence.tokens) == 14


def test_len_empty():
    """
    Test if an empty sentence is properly parsed.
    """
    source = ""
    sentence = parse_sentence(source)

    assert len(sentence.tokens) == 0


def test_output():
    """
    Test if the sentence output is properly produced.
    """
    source = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )
    sentence = parse_sentence(source)

    assert sentence.conll() == source


def test_output_comments():
    """
    Test the sentence output for a singleton comment, and the comment order is kept.
    """
    source = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "# newpar id\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )
    sentence = parse_sentence(source)

    assert sentence.conll() == source


def test_modified_output():
    """
    Test if the sentence is properly outputted after changing the annotation.
    """
    source = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )
    sentence = parse_sentence(source)

    sentence.meta["sent_id"] = "fr-ud-dev_00231"
    sentence.tokens[12].lemma = "facultés"
    sentence.tokens[12].upos = "NOUN"

    sentence.tokens[12].feats["Number"] = set()
    sentence.tokens[12].feats["Number"].add("Fem")

    output = (
        "# sent_id = fr-ud-dev_00231\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	facultés	NOUN	_	Number=Fem	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )

    assert sentence.conll() == output


def test_change_comments():
    """
    Test that comment values (other than text or id) can be changed through the
    meta api.
    """
    source = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )

    expected = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "# newpar id = xyz-1\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )

    sentence = parse_sentence(source)
    sentence.meta["newpar id"] = "xyz-1"

    assert sentence.conll() == expected


def test_add_comments():
    """
    Test that comment values (other than text) can be added through the meta
    api.
    """
    source = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )

    expected = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "# x-coord = 2\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )

    sentence = parse_sentence(source)
    sentence.meta["x-coord"] = "2"

    assert sentence.conll() == expected


def test_remove_comments():
    """
    Test that comments can be removed from the sentence and the serialization is as expected.
    """
    source = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "# x-coord = 2\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )

    expected = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )

    sentence = parse_sentence(source)
    del sentence.meta["x-coord"]

    assert sentence.conll() == expected


def test_singleton_comment():
    """
    Test that a singleton comment is properly output.
    """
    source = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )

    expected = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "# foreign\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )

    sentence = parse_sentence(source)
    sentence.meta["foreign"] = None

    assert sentence.conll() == expected


def test_no_id():
    """
    Test that a sentence can be properly constructed with no id.
    """
    source = (
        "# newpar id\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )
    sentence = parse_sentence(source)

    assert "sent_id" not in sentence.meta


def test_no_id_singleton():
    """
    Test that a sentence can be properly constructed with no id.
    """
    source = (
        "# newpar id\n"
        "# sent_id\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )
    sentence = parse_sentence(source)

    assert sentence.meta["sent_id"] is None


def test_no_text():
    """
    Test that a sentence can be properly constructed with no text field.
    """
    source = (
        "# newpar id\n"
        "# sent_id =\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )
    sentence = parse_sentence(source)

    assert "text" not in sentence.meta


def test_no_text_singleton():
    """
    Test that a sentence can be properly constructed with no text field.
    """
    source = (
        "# newpar id\n"
        "# sent_id =\n"
        "# text\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )
    sentence = parse_sentence(source)

    assert sentence.meta["text"] is None


def test_invalid_sentence_by_token():
    """
    Test that an invalid token results in an invalid sentence.
    """
    source = (
        "# newpar id\n"
        "# sent_id =\n"
        "# text =\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )

    with pytest.raises(ValueError):
        parse_sentence(source)


def test_conll_error():
    """
    Test that an error in serialization with a Token surfaces as a FormatError.
    """
    source = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )
    sent = parse_sentence(source)
    sent.tokens[0].misc = True

    with pytest.raises(FormatError):
        sent.conll()


def test_sentence_repr():
    """
    Test that a sentence can be represented as a string.
    """
    source = (
        "# sent_id = fr-ud-dev_00002\n"
        "# text = Les études durent six ans mais leur contenu diffère donc selon les Facultés.\n"
        "1	Les	le	DET	_	Definite=Def|Gender=Fem|Number=Plur|PronType=Art	2	det	_	_\n"
        "2	études	étude	NOUN	_	Gender=Fem|Number=Plur	3	nsubj	_	_\n"
        "3	durent	durer	VERB	_	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_\n"
        "4	six	six	NUM	_	_	5	nummod	_	_\n"
        "5	ans	an	NOUN	_	Gender=Masc|Number=Plur	3	obj	_	_\n"
        "6	mais	mais	CCONJ	_	_	9	cc	_	_\n"
        "7	leur	son	DET	_	Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs	8	det	_	_\n"
        "8	contenu	contenu	NOUN	_	Gender=Masc|Number=Sing	9	nsubj	_	_\n"
        "9	diffère	différer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	conj	_	_\n"
        "10	donc	donc	ADV	_	_	9	advmod	_	_\n"
        "11	selon	selon	ADP	_	_	13	case	_	_\n"
        "12	les	le	DET	_	Definite=Def|Number=Plur|PronType=Art	13	det	_	_\n"
        "13	Facultés	Facultés	PROPN	_	_	9	obl	_	SpaceAfter=No\n"
        "14	.	.	PUNCT	_	_	3	punct	_	_"
    )
    sent = parse_sentence(source)
    assert type(repr(sent)) is str