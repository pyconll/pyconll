import os

from pyconllu.unit import Conllu
from tests.util import fixture_location


def test_creation():
    """
    Test the basic creation of a Conllu object.
    """
    with open(fixture_location('basic.conllu')) as f:
        conllu = Conllu(f)

    assert len(conllu) == 4

    assert len(conllu[0]) == 10
    assert conllu[0].id == 'fr-ud-dev_00001'

    assert len(conllu[1]) == 14
    assert conllu[1].id == 'fr-ud-dev_00002'

    assert len(conllu[2]) == 9
    assert conllu[2].id == 'fr-ud-dev_00003'

    assert len(conllu[3]) == 52
    assert conllu[3].id == 'fr-ud-dev_00004'


def test_no_ending_newline():
    """
    Test correct creation when the ending of the file ends in no newline.
    """
    with open(fixture_location('no_newline.conllu')) as f:
        conllu = Conllu(f)

    assert len(conllu) == 3

    assert len(conllu[0]) == 10
    assert conllu[0].id == 'fr-ud-dev_00001'

    assert len(conllu[1]) == 14
    assert conllu[1].id == 'fr-ud-dev_00002'

    assert len(conllu[2]) == 9
    assert conllu[2].id == 'fr-ud-dev_00003'


def test_many_newlines():
    """
    Test correct Conllu parsing when there are too many newlines.
    """
    with open(fixture_location('many_newlines.conllu')) as f:
        conllu = Conllu(f)

    assert len(conllu) == 4

    assert len(conllu[0]) == 10
    assert conllu[0].id == 'fr-ud-dev_00001'

    assert len(conllu[1]) == 14
    assert conllu[1].id == 'fr-ud-dev_00002'

    assert len(conllu[2]) == 9
    assert conllu[2].id == 'fr-ud-dev_00003'

    assert len(conllu[3]) == 52
    assert conllu[3].id == 'fr-ud-dev_00004'


def test_numeric_indexing():
    """
    Test the ability to index sentences through their numeric position.
    """
    with open(fixture_location('basic.conllu')) as f:
        conllu = Conllu(f)

    assert len(conllu[0]) == 10
    assert conllu[0].id == 'fr-ud-dev_00001'


def test_id_indexing():
    """
    Test the ability to index sentences through their ids.
    """
    with open(fixture_location('basic.conllu')) as f:
        conllu = Conllu(f)

    assert len(conllu['fr-ud-dev_00001']) == 10
    assert conllu['fr-ud-dev_00001'].id == 'fr-ud-dev_00001'


def test_slice_indexing():
    """
    Test the ability to slice up a Conllu object and its result.
    """
    with open(fixture_location('long.conllu')) as f:
        conllu = Conllu(f)

    every_3 = conllu['fr-ud-test_00002':'fr-ud-test_00008':3]

    assert len(every_3) == 2
    assert every_3[0].id == 'fr-ud-test_00002'
    assert len(every_3['fr-ud-test_00005']) == 38

    every_2 = conllu[1:6:2]
    assert len(every_2) == 3


def test_string_output():
    """
    Test that the strings are properly created.
    """
    with open(fixture_location('basic.conllu')) as f:
        contents = f.read()
        f.seek(0)
        conllu = Conllu(f)

    assert contents == conllu.conllu()


def test_writing_output():
    """
    Test that CoNLL-U files are properly created.
    """
    with open(fixture_location('basic.conllu')) as f:
        contents_basic = f.read()
        f.seek(0)
        conllu = Conllu(f)

    output_loc = fixture_location('output.conllu')
    with open(output_loc, 'w') as f:
        conllu.write(f)

    with open(output_loc) as f:
        contents_write = f.read()
    os.remove(fixture_location('output.conllu'))

    assert contents_basic == contents_write


def test_sentence_line_numbers():
    """
    Test that the CoNLL-U files properly associate line numbers.
    """
    sentence_bounds = [(1, 12), (14, 29), (31, 41), (43, 96)]

    with open(fixture_location('basic.conllu')) as f:
        c = Conllu(f)

    for i, sent in enumerate(c):
        cur_bounds = sentence_bounds[i]
        assert sent.start_line_number == cur_bounds[0]
        assert sent.end_line_number == cur_bounds[1]


def test_sentence_line_numbers_extra_newlines():
    """
    Test that the CoNLL-U files properly read in the sentence lines when there
    are extra newlines.
    """
    sentence_bounds = [(3, 14), (16, 31), (34, 44), (46, 99)]

    with open(fixture_location('many_newlines.conllu')) as f:
        c = Conllu(f)

    for i, sent in enumerate(c):
        cur_bounds = sentence_bounds[i]
        assert sent.start_line_number == cur_bounds[0]
        assert sent.end_line_number == cur_bounds[1]


def test_par_and_doc_id_basic():
    """
    Test that the paragraph and document ids are properly associated with the
    Sentences.
    """
    with open(fixture_location('par_doc_ids_basic.conllu')) as f:
        c = Conllu(f)

    expected_doc_ids = ['2', '2', '1', '1']
    actual_doc_ids = [s.doc_id for s in c]

    assert expected_doc_ids == actual_doc_ids


def test_par_and_doc_id_long():
    """
    Test that the paragraph and document ids are properly associated with the
    Sentences.
    """
    with open(fixture_location('par_doc_ids_long.conllu')) as f:
        c = Conllu(f)

    expected_doc_ids = [
        None, None, 'abc-1', 'abc-1', 'xyz-2', 'xyz-2', 'xyz-2', None, None
    ]
    actual_doc_ids = [s.doc_id for s in c]

    expected_par_ids = [None, None, None, '70', '70', None, '71', '71', '71']
    actual_par_ids = [s.par_id for s in c]

    assert expected_doc_ids == actual_doc_ids
    assert expected_par_ids == actual_par_ids
