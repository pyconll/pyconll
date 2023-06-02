"""
Module for helping test Token related functionality.
"""


def assert_token_equivalence(token1, token2):
    """
    Asserts that two tokens are equivalent in all their members.

    Args:
        token1: One of the tokens to compare.
        token2: The second token to compare against the first for equality.
    """
    assert_token_members(token1, token2.id, token2.form, token2.lemma,
                         token2.upos, token2.xpos, token2.feats, token2.head,
                         token2.deprel, token2.deps, token2.misc)


def assert_token_members(token, id, form, lemma, upos, xpos, feats, head,
                         deprel, deps, misc):
    """
    Asserts the value of all the members for the given token.

    Args:
        token: The token to assert the value of.
        id: The token id to assert.
        form: The word form.
        lemma: The lemma.
        upos: The Universal Dependencies part of speech tag.
        xpos: The language specific part of speech tag.
        feats: The features.
        head: The id of the governor.
        deprel: The relationship between the head and the child.
        deps: Enhanced universal dependencies.
        misc: Miscellaneous associated attributes.
    """
    # NOTE: This uses equality for None comparison, is it worth doing differently?
    assert token.id == id
    assert token.form == form
    assert token.lemma == lemma
    assert token.upos == upos
    assert token.xpos == xpos
    assert token.feats == feats
    assert token.head == head
    assert token.deprel == deprel
    assert token.deps == deps
    assert token.misc == misc
