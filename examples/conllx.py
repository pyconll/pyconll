#
# Create a Token schema for parsing CoNLL 2003 data.
#


import sys
from typing import Optional
from pyconll.parser import Parser
from pyconll.schema import TokenSchema, nullable, unique_array
from pyconll.serializer import Serializer


class TokenX(TokenSchema):
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

parser = Parser(TokenX)
serializer = Serializer(TokenX)

sentences = parser.load_from_file("eng.conllx")
sentences[0].tokens[0].feats.add("first")
serializer.write_corpus(sentences, sys.stdout)