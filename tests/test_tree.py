import pytest

from pyconll import tree
from pyconll.tree import Tree, _TreeBuilder

from tests.unit.util import parse_sentence
from tests.util import assert_tree_structure


def test_minimal_tree_creation():
    """
    Test creating the minimal tree using the constructor.
    """
    t = Tree(None)

    assert t.data is None
    assert t.parent is None
    assert len(t) == 0


def test_data_read_only():
    """
    Test that the data on a Tree cannot be assigned after construction.
    """
    t = Tree(None)
    with pytest.raises(AttributeError):
        t.data = 0


def test_parent_read_only():
    """
    Test that the parent field cannot be assigned after construction.
    """
    t = Tree(None)
    with pytest.raises(AttributeError):
        t.parent = None


def test_get_children():
    """
    Test that we can properly retreive children from a tree by index.
    """
    builder = _TreeBuilder()
    builder.create_root(1)
    builder.add_child(7)
    builder.add_child(2, move=True)
    builder.add_child(13)
    t = builder.build()

    assert t[0].data == 7
    assert t[1].data == 2
    assert t[1][0].data == 13


def test_iter_children():
    """
    Test that we can properly iterate over the children of a tree.
    """
    builder = _TreeBuilder()
    builder.create_root(0)

    data = list(range(2, 15, 3))
    for datum in data:
        builder.add_child(datum)
    t = builder.build()

    for i, child in enumerate(t):
        assert child.data == data[i]


def test_len_children():
    """
    Test that we can properly get the number of children.
    """
    builder = _TreeBuilder()
    builder.create_root(0)

    data = list(range(2, 15, 3))
    subdata = [0, 1, 2, 3, 4]
    for datum in data:
        builder.add_child(datum, move=True)

        for subdatum in subdata:
            builder.add_child(subdatum)

        builder.move_to_parent()
    t = builder.build()

    assert len(t) == len(data)
    for child in t:
        assert len(child) == len(subdata)


def test_parent_assigment():
    """
    Test that children tree's parents are properly assigned.
    """
    builder = _TreeBuilder()
    builder.create_root(0)
    builder.add_child(2, move=True)
    builder.add_child(13)
    builder.move_to_parent()
    builder.add_child(7)

    t = builder.build()

    assert t.parent is None
    assert t[0].parent == t
    assert t[1].parent == t
    assert t[0][0].parent == t[0]


def test_after_creation_copy():
    """
    Test that a single TreeBuilder can be used multiple times properly.
    """
    builder = _TreeBuilder()
    builder.create_root(0)
    builder.add_child(2, move=True)
    builder.add_child(13)
    builder.move_to_parent()
    builder.add_child(7)

    t1 = builder.build()

    builder.move_to_root()
    builder.set_data(4)
    builder.add_child(3, move=True)
    builder.add_child(15)

    t2 = builder.build()

    assert t2 is not t1
    assert t2[0] is not t1[0]
    assert t2[0][0] is not t1[0][0]
    assert t2[1] is not t1[1]

    assert t2.data == 4
    assert t2[0].data == 2
    assert t2[0][0].data == 13
    assert t2[1].data == 7
    assert t2[2].data == 3
    assert t2[2][0].data == 15

    assert len(t2) == 3
    assert len(t2[0]) == 1
    assert len(t2[1]) == 0
    assert len(t2[2]) == 1


def test_cannot_operate_on_rootless():
    """
    Verify that operations do not work on a TreeBuilder when no root is created.
    """
    builder = _TreeBuilder()

    with pytest.raises(ValueError):
        builder.move_to_root()

    with pytest.raises(ValueError):
        builder.move_to_parent()

    with pytest.raises(ValueError):
        builder.build()


def test_cannot_move_up_on_root():
    """
    Test that when at the root node, the builder cannot move up to a parent.
    """
    builder = _TreeBuilder()

    builder.create_root(0)

    with pytest.raises(ValueError):
        builder.move_to_parent()


def test_cannot_move_out_of_range():
    """
    Test that the builder cannot move to a child that is out of index.
    """
    builder = _TreeBuilder()

    builder.create_root(0)
    builder.add_child(5)

    with pytest.raises(IndexError):
        builder.move_to_child(3)


def test_cannot_remove_out_of_range():
    """
    Test that the builder cannot remove a child it does not have.
    """
    builder = _TreeBuilder()

    builder.create_root(0)
    builder.add_child(5)

    with pytest.raises(IndexError):
        builder.remove_child(5)


def test_on_copy_not_on_root():
    """
    Test that the current pointer is relatively correct after a copy operation.
    """
    builder = _TreeBuilder()
    builder.create_root(0)
    builder.add_child(5)
    builder.add_child(6, move=True)

    _ = builder.build()
    builder.add_child(7)

    t = builder.build()
    assert_tree_structure(t, {(): 0, (0,): 5, (1,): 6, (1, 0): 7})


def test_to_tree_standard_sentence():
    """
    Test that a normal sentence can be parsed properly.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# text = Mais comment faire ?\n'
              '1	Mais	mais	CCONJ	_	_	3	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = parse_sentence(source)
    st = tree.from_conllu_tokens(sentence.tokens)

    assert_tree_structure(
        st, {
            (): sentence.tokens[2],
            (0, ): sentence.tokens[0],
            (1, ): sentence.tokens[1],
            (2, ): sentence.tokens[3]
        })


def test_to_tree_token_with_no_head():
    """
    Test that a sentence with a token with no head results in error.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# text = Mais comment faire ?\n'
              '1	Mais	mais	CCONJ	_	_	_	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = parse_sentence(source)
    with pytest.raises(ValueError):
        tree.from_conllu_tokens(sentence.tokens)


def test_to_tree_empty_node_exception():
    """
    Test tree parsing for sentence with an empty node.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# text = Mais comment faire ?\n'
              '1	Mais	mais	CCONJ	_	_	3	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '3.1	test	test	VERB	_	_	_	_	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = parse_sentence(source)
    st = tree.from_conllu_tokens(sentence.tokens)

    assert_tree_structure(
        st, {
            (): sentence.tokens[2],
            (0, ): sentence.tokens[0],
            (1, ): sentence.tokens[1],
            (2, ): sentence.tokens[4]
        })


def test_to_tree_no_root_token():
    """
    Test that a sentence with no root token results in error.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# text = Mais comment faire ?\n'
              '1	Mais	mais	CCONJ	_	_	_	cc	_	_\n'
              '2	comment	comment	ADV	_	_	3	advmod	_	_\n'
              '3	faire	faire	VERB	_	VerbForm=Inf	1	root	_	_\n'
              '4	?	?	PUNCT	_	_	3	punct	_	_\n')
    sentence = parse_sentence(source)
    with pytest.raises(ValueError):
        tree.from_conllu_tokens(sentence.tokens)


def test_to_tree_multiword_present():
    """
    Test that a normal sentence can be parsed properly.
    """
    source = ('# sent_id = fr-ud-dev_00003\n'
              '# text = Mais comment faire ?\n'
              '1	Mais	mais	CCONJ	_	_	5	cc	_	_\n'
              '2	comment	comment	ADV	_	_	5	advmod	_	_\n'
              '3-4	du	_	_	_	_	_	_	_	_\n'
              '3	de	de	ADP	_	_	4	nmod	_	_\n'
              '4	le	le	DET	_	_	5	det	_	_\n'
              '5	faire	faire	VERB	_	VerbForm=Inf	0	root	_	_\n'
              '6	?	?	PUNCT	_	_	5	punct	_	_\n')
    sentence = parse_sentence(source)
    st = tree.from_conllu_tokens(sentence.tokens)

    assert_tree_structure(
        st, {
            (): sentence.tokens[5],
            (0, ): sentence.tokens[0],
            (1, ): sentence.tokens[1],
            (2, ): sentence.tokens[4],
            (3, ): sentence.tokens[6],
            (2, 0): sentence.tokens[3]
        })


def test_to_tree_multi_level():
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
    sentence = parse_sentence(source)
    st = tree.from_conllu_tokens(sentence.tokens)

    assert_tree_structure(
        st, {
            (): sentence.tokens[2],
            (0, ): sentence.tokens[1],
            (1, ): sentence.tokens[4],
            (2, ): sentence.tokens[8],
            (3, ): sentence.tokens[13],
            (0, 0): sentence.tokens[0],
            (1, 0): sentence.tokens[3],
            (2, 0): sentence.tokens[5],
            (2, 1): sentence.tokens[7],
            (2, 2): sentence.tokens[9],
            (2, 3): sentence.tokens[12],
            (2, 1, 0): sentence.tokens[6],
            (2, 3, 0): sentence.tokens[10],
            (2, 3, 1): sentence.tokens[11]
        })


def test_tree_empty_sentence():
    """
    Test that an empty sentence throws an error on Tree creation.
    """
    source = ''
    sentence = parse_sentence(source)

    with pytest.raises(ValueError):
        tree.from_conllu_tokens(sentence.tokens)


def test_tree_no_extra_nodes():
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
    sentence = parse_sentence(source)
    st = tree.from_conllu_tokens(sentence.tokens)

    count = 0
    nodes = [st]
    while len(nodes) > 0:
        count += 1
        node = nodes.pop()

        for child in node:
            nodes.append(child)

    assert len(sentence.tokens) == count