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
