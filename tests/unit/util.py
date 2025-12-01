"""
Module that collects various test related functionality.
"""

from pathlib import Path
from typing import Optional, OrderedDict

from pyconll.conllu import Sentence, Token, conllu
from pyconll.schema import SentenceBase
from pyconll.tree import Tree


def fixture_location(name: str) -> Path:
    """
    Get the file location of the fixture with the given name.
    """
    return Path(__file__).parent / "fixtures" / name


def assert_tree_structure[T](tree: Tree[T], children_paths: dict[tuple[int, ...], T]):
    """
    Assert a tree structure from tree node paths to values.

    Args:
        tree: The tree whose structure to inspect.
        children_paths: A dictionary from child indices to token indices.
    """
    for path, value in children_paths.items():
        cur = tree
        for component in path:
            cur = cur[component]

        assert cur.data == value


def assert_token_equivalence(token1: Token, token2: Token) -> None:
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


def assert_token_members(
    token: Token,
    id: str,
    form: Optional[str],
    lemma: Optional[str],
    upos: Optional[str],
    xpos: Optional[str],
    feats: dict[str, set[str]],
    head: Optional[str],
    deprel: Optional[str],
    deps: dict[str, tuple[str, ...]],
    misc: dict[str, Optional[set[str]]],
) -> None:
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


def parse_sentence(lines: str) -> Sentence[Token]:
    """
    Parse a single sentence, and assert that only one sentence can be extracted from the source.

    Args:
        lines: The lines to parse a sentence from.

    Returns:
        The singular parsed Sentence that can be constructed from the line source.
    """
    sentences = conllu.load_from_string(lines)

    if len(sentences) != 1:
        raise RuntimeError("Expected exactly one sentence in the lines given.")

    return sentences[0]


class InMemorySentence[T](SentenceBase[T]):
    __slots__ = ["meta", "tokens"]

    def __init__(self) -> None:
        self.meta: OrderedDict[str, Optional[str]] = OrderedDict()
        self.tokens: list[T] = []

    def __accept_meta__(self, key: str, value: Optional[str]) -> None:
        self.meta[key] = value

    def __accept_token__(self, t: T) -> None:
        self.tokens.append(t)

    def __finalize__(self) -> None: ...
