"""
Tests for tree creation from CoNLL-U formatted sentences.
"""

import pytest

from pyconll import conllu

from tests.unit.util import assert_tree_structure, parse_sentence


def test_to_tree_standard_sentence():
    """
    Test that a normal sentence can be parsed properly.
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
    st = conllu.tree_from_tokens(sentence.tokens)

    assert_tree_structure(
        st,
        {
            (): sentence.tokens[2],
            (0,): sentence.tokens[0],
            (1,): sentence.tokens[1],
            (2,): sentence.tokens[3],
        },
    )


def test_to_tree_token_with_no_head():
    """
    Test that a sentence with a token with no head results in error.
    """
    source = (
        "# sent_id = fr-ud-dev_00003\n"
        "# text = Mais comment faire ?\n"
        "1	Mais	mais	CCONJ	_	_	_	cc	_	_\n"
        "2	comment	comment	ADV	_	_	3	advmod	_	_\n"
        "3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n"
        "4	?	?	PUNCT	_	_	3	punct	_	_\n"
    )
    sentence = parse_sentence(source)
    with pytest.raises(ValueError):
        conllu.tree_from_tokens(sentence.tokens)


def test_to_tree_empty_node_exception():
    """
    Test tree parsing for sentence with an empty node.
    """
    source = (
        "# sent_id = fr-ud-dev_00003\n"
        "# text = Mais comment faire ?\n"
        "1	Mais	mais	CCONJ	_	_	3	cc	_	_\n"
        "2	comment	comment	ADV	_	_	3	advmod	_	_\n"
        "3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n"
        "3.1	test	test	VERB	_	_	_	_	_	_\n"
        "4	?	?	PUNCT	_	_	3	punct	_	_\n"
    )
    sentence = parse_sentence(source)
    st = conllu.tree_from_tokens(sentence.tokens)

    assert_tree_structure(
        st,
        {
            (): sentence.tokens[2],
            (0,): sentence.tokens[0],
            (1,): sentence.tokens[1],
            (2,): sentence.tokens[4],
        },
    )


def test_to_tree_no_root_token():
    """
    Test that a sentence with no root token results in error.
    """
    source = (
        "# sent_id = fr-ud-dev_00003\n"
        "# text = Mais comment faire ?\n"
        "1	Mais	mais	CCONJ	_	_	_	cc	_	_\n"
        "2	comment	comment	ADV	_	_	3	advmod	_	_\n"
        "3	faire	faire	VERB	_	VerbForm=Inf	1	root	_	_\n"
        "4	?	?	PUNCT	_	_	3	punct	_	_\n"
    )
    sentence = parse_sentence(source)
    with pytest.raises(ValueError):
        conllu.tree_from_tokens(sentence.tokens)


def test_to_tree_multiword_present():
    """
    Test that a normal sentence can be parsed properly.
    """
    source = (
        "# sent_id = fr-ud-dev_00003\n"
        "# text = Mais comment faire ?\n"
        "1	Mais	mais	CCONJ	_	_	5	cc	_	_\n"
        "2	comment	comment	ADV	_	_	5	advmod	_	_\n"
        "3-4	du	_	_	_	_	_	_	_	_\n"
        "3	de	de	ADP	_	_	4	nmod	_	_\n"
        "4	le	le	DET	_	_	5	det	_	_\n"
        "5	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n"
        "6	?	?	PUNCT	_	_	5	punct	_	_\n"
    )
    sentence = parse_sentence(source)
    st = conllu.tree_from_tokens(sentence.tokens)

    assert_tree_structure(
        st,
        {
            (): sentence.tokens[5],
            (0,): sentence.tokens[0],
            (1,): sentence.tokens[1],
            (2,): sentence.tokens[4],
            (3,): sentence.tokens[6],
            (2, 0): sentence.tokens[3],
        },
    )


def test_to_tree_multi_level():
    """
    Test a sentence with several levels of dependencies deep is properly parsed.
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
    st = conllu.tree_from_tokens(sentence.tokens)

    assert_tree_structure(
        st,
        {
            (): sentence.tokens[2],
            (0,): sentence.tokens[1],
            (1,): sentence.tokens[4],
            (2,): sentence.tokens[8],
            (3,): sentence.tokens[13],
            (0, 0): sentence.tokens[0],
            (1, 0): sentence.tokens[3],
            (2, 0): sentence.tokens[5],
            (2, 1): sentence.tokens[7],
            (2, 2): sentence.tokens[9],
            (2, 3): sentence.tokens[12],
            (2, 1, 0): sentence.tokens[6],
            (2, 3, 0): sentence.tokens[10],
            (2, 3, 1): sentence.tokens[11],
        },
    )


def test_tree_empty_sentence():
    """
    Test that an empty sentence throws an error on Tree creation.
    """
    source = ""
    sentence = parse_sentence(source)

    with pytest.raises(ValueError):
        conllu.tree_from_tokens(sentence.tokens)


def test_tree_no_extra_nodes():
    """
    Test that there are the right amount of nodes in the tree.
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
    st = conllu.tree_from_tokens(sentence.tokens)

    count = 0
    nodes = [st]
    while len(nodes) > 0:
        count += 1
        node = nodes.pop()

        for child in node:
            nodes.append(child)

    assert len(sentence.tokens) == count
