#!/usr/bin/env python

#
# Change the annotation of a certain ngram. In this case, change any instances
# of 'de plus' (FR) to a fixed annotation if they were previously connected.
# The condition of having been previously connected requires conditions that are
# difficult for most other tools I've seen to handle inside their DSL.
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
for sentence, i in pyconll.util.find_ngrams(corpus, NGRAM)
    ngram = sentence[i:i + len(NGRAM)]

    # For each ngram check if the were related before. As a heuristic for
    # false positives, do not want to include ngrams that were not already
    # related.
    de_token, plus_token = ngram

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
