import pytest

from pyconll.tree import SentenceTree
from pyconll.unit import Sentence


def assert_tree_structure(sentence, tree, root_token, children_paths):
    """
    Assert a tree structure from tree node paths to sentence tokens.

    Args:
        sentence: The sentence that the tree is created from.
        tree: The tree whose structure to inspect.
        root_token: The root token of the tree.
        children_paths: A dictionary from child indices to token indices.
    """
    assert tree.data == root_token

    for path, token_key in children_paths.items():
        cur = tree
        for component in path:
            cur = cur[component]

        assert cur.data == sentence[token_key]


def test_standard_sentence():
    """
    Test that a normal sentence can be parsed properly.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# text = Mais comment faire ?\n'
              '1	Mais	mais	CCONJ	_	_	3	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = Sentence(source)

    st = SentenceTree(sentence)

    assert st.sentence == sentence

    assert_tree_structure(st.sentence, st.tree, sentence[2], {
        (0, ): 0,
        (1, ): 1,
        (2, ): 3
    })


def test_multi_level():
    """
    Test a sentence with several levels of dependencies deep is properly parsed.
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
    st = SentenceTree(sentence)

    assert_tree_structure(
        st.sentence, st.tree, sentence[2], {
            (0, ): 1,
            (1, ): 4,
            (2, ): 8,
            (3, ): 13,
            (0, 0): 0,
            (1, 0): 3,
            (2, 0): 5,
            (2, 1): 7,
            (2, 2): 9,
            (2, 3): 12,
            (2, 1, 0): 6,
            (2, 3, 0): 10,
            (2, 3, 1): 11
        })


def test_empty_sentence():
    """
    Test that an empty sentence is properly parsed.
    """
    source = ''
    sentence = Sentence(source)
    st = SentenceTree(sentence)

    assert st.tree.data == None
    assert st.tree.children == []


def test_no_extra_nodes():
    """
    Test that there are the right amount of nodes in the tree.
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
    st = SentenceTree(sentence)

    count = 0
    nodes = [st.tree]
    while len(nodes) > 0:
        count += 1
        node = nodes.pop()

        for child in node:
            nodes.append(child)

    assert len(sentence) == count
