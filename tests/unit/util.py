"""
Module for helping test Token related functionality.
"""

from typing import Iterable

from pyconll._parser import iter_sentences
from pyconll.unit.sentence import Sentence


def assert_token_equivalence(token1, token2):
    """
    Asserts that two tokens are equivalent in all their members.

    Args:
        token1: One of the tokens to compare.
        token2: The second token to compare against the first for equality.
    """
    assert_token_members(
        token1,
        token2.id,
        token2.form,
        token2.lemma,
        token2.upos,
        token2.xpos,
        token2.feats,
        token2.head,
        token2.deprel,
        token2.deps,
        token2.misc,
    )


def assert_token_members(token, id, form, lemma, upos, xpos, feats, head, deprel, deps, misc):
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


def parse_sentence(lines: str) -> Sentence:
    """
    Parse a single sentence, and assert that only one sentence can be extracted from the source.

    Args:
        lines: The lines to parse a sentence from.

    Returns:
        The singular parsed Sentence that can be constructed from the line source.
    """
    gen = iter_sentences(lines.split("\n"))
    sentence = next(gen)

    raised = False
    try:
        next(gen)
    except StopIteration:
        raised = True

    if not raised:
        raise RuntimeError("Expected only one sentence in the lines given.")

    return sentence
