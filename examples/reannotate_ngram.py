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


def find_ngrams(sentence, ngram, case_sensitive=True):
    """
    Find the occurences of the ngram in the provided sentence.

    NOTE: This method is not really tested. Please do not use it in production
    code without first testing it or wait until I put into an auxiliary util
    package.

    Args:
    sentence: The sentence in which to search for the ngram.
    ngram: The ngram to search for. A random access iterator.
    case_sensitive: Flag to indicate if the ngram search should be case sensitive.

    Returns:
    An iterator over the ngrams in the sentence.
    """
    ngram_start = -1
    cur_ngram_idx = 0
    i = 0

    while i < range(len(sentence)):
        if ngram_start >= 0:
            cur_index = i + ngram_start
        else:
            cur_index = i
        token = sentence[cur_index]

        if not case_sensitive:
            cased_form = token.form.lower()
            cased_ngram = ngram[cur_ngram_idx].lower()
        else:
            cased_form = token.form
            cased_ngram = ngram[cur_ngram_idx]

        if cased_form == cased_ngram:
            if cur_ngram_idx == 0:
                ngram_start = i

            cur_ngram_idx += 1

            if cur_ngram_idx == len(ngram):
                yield sentence[ngram_start:cur_index + 1]

                ngram_start = -1
                cur_ngram_idx = 0
        else:
            ngram_start = -1
            cur_ngram_idx = 0

        if ngram_start < 0:
            i += 1
            

parser = argparse.ArgumentParser()
parser.add_argument('filename', help='The name of the file to transform')
args = parser.parse_args()

corpus = pyconll.load_from_filename(args.filename)
for sentence in corpus:
    for ngram in find_ngrams(sentence, NGRAM, case_sensitive=False):
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


corpus.conll()
