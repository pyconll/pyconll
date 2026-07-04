#
# Create a Token schema for parsing CoNLL 2003 data.
#


import sys
from typing import Optional

from pyconll.format import Format
from pyconll.schema import field, nullable, tokenspec, unique_array
from pyconll.shared import Sentence


@tokenspec
class TokenX:
    id: int
    form: str
    lemma: str
    cpostag: str
    postag: str
    feats: set[str] = field(unique_array(str, "|", "_"))
    head: int
    deprel: str
    phead: Optional[int] = field(nullable(int, "_"))
    pdeprel: Optional[str] = field(nullable(str, "_"))


conllx = Format(TokenX, Sentence[TokenX], comment_marker="#", delimiter="\t")

sentences = conllx.load_from_file("eng.conllx")
sentences[0].tokens[0].feats.add("first")
conllx.write_corpus(iter(sentences), sys.stdout)
