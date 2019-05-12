#!/usr/bin/env python

#
# Change the annotation of a certain ngram. In this case, change any instances
# of 'de plus' (FR) to a fixed annotation if they were previously connected.
# A variation of this, where right or left headedness of a relation is
# important can be quite difficult or impossible to express in some DSL query
# languages for CoNLL-U.
#
# Format:
#   reannotate_ngram.py filename > transform.conll

import argparse

import pyconll

NGRAM = ('de', 'plus')

parser = argparse.ArgumentParser()
parser.add_argument('filename', help='The name of the file to transform')
args = parser.parse_args()

corpus = pyconll.load_from_filename(args.filename)
for sentence, i, tokens in pyconll.util.find_ngrams(corpus, NGRAM)
    # Deconstruct the tokens list into the separate tokens.
    de_token, plus_token = tokens 

    # If the two tokens have a direct dependency between them, then assign "de"
    # as the governer, and "plus" as the child, with "fixed" as the dependency
    # between them.
    if de_token.head == plus_token.id:
        parent_index = plus_token.head
        parent_deprel = plus_token.deprel

        de_token.head = parent_index
        de_token.deprel = parent_deprel

        plus_token.head = de_token.id
        plus_token.deprel = 'fixed'
    elif de_token.id == plus_token.head:
        plus_token.deprel = 'fixed'


# Print out result to stdout, which can then be redirected.
print(corpus.conll())
