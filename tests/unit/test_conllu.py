import os

from pyconllu.unit import Conllu


def _fixture_location(name):
    """
    Get the file location of the fixture with the given name.
    """
    return os.path.join(os.path.dirname(__file__), 'fixtures', name)


def test_creation():
    """
    Test the basic creation of a Conllu object.
    """
    with open(_fixture_location('basic.conllu')) as f:
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
    with open(_fixture_location('no_newline.conllu')) as f:
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
    with open(_fixture_location('many_newlines.conllu')) as f:
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
    with open(_fixture_location('basic.conllu')) as f:
        conllu = Conllu(f)

    assert len(conllu[0]) == 10
    assert conllu[0].id == 'fr-ud-dev_00001'


def test_id_indexing():
    """
    Test the ability to index sentences through their ids.
    """
    with open(_fixture_location('basic.conllu')) as f:
        conllu = Conllu(f)

    assert len(conllu['fr-ud-dev_00001']) == 10
    assert conllu['fr-ud-dev_00001'].id == 'fr-ud-dev_00001'


def test_slice_indexing():
    """
    Test the ability to slice up a Conllu object and its result.
    """
    with open(_fixture_location('long.conllu')) as f:
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
    with open(_fixture_location('basic.conllu')) as f:
        contents = f.read()
        f.seek(0)
        conllu = Conllu(f)

    assert contents == conllu.conllu()


def test_writing_output():
    """
    Test that CoNLL-U files are properly created.
    """
    with open(_fixture_location('basic.conllu')) as f:
        contents_basic = f.read()
        f.seek(0)
        conllu = Conllu(f)

    output_loc = _fixture_location('output.conllu')
    with open(output_loc, 'w') as f:
        conllu.write(f)

    with open(output_loc) as f:
        contents_write = f.read()
    os.remove(_fixture_location('output.conllu'))

    assert contents_basic == contents_write
