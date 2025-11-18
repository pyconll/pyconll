#
# Create a Token schema for parsing CoNLL 2003 data.
#


import sys
from typing import Optional
from pyconll.format import Format
from pyconll.schema import tokenspec, nullable, unique_array


@tokenspec
class TokenX:
    id: int
    form: str
    lemma: str
    cpostag: str
    postag: str
    feats: set[str] = unique_array(str, "|", "_")
    head: int
    deprel: str
    phead: Optional[int] = nullable(int, "_")
    pdeprel: Optional[str] = nullable(str, "_")


conllx = Format(TokenX, comment_marker="#", delimiter="\t")

sentences = conllx.load_from_file("eng.conllx")
sentences[0].tokens[0].feats.add("first")
conllx.write_corpus(sentences, sys.stdout)
