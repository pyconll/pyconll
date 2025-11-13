#
# Reassign all occurrences of 'France', 'Spain', and 'Germany' with a new country
# marker in the MISC field, and ensure that they are tagged as a PROPN. Output
# the new CoNLL data to stdout.
#
# Format:
#   reassign_proper_noun_pos.py filename > transform.conll
#

import argparse
import sys

from pyconll.conllu import conllu

COUNTRIES = set(("france", "spain", "germany"))

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="The name of the file to transform")
args = parser.parse_args()

corpus = conllu.load_from_file(args.filename)
for sentence in corpus:
    for token in sentence.tokens:
        if token.form.lower() in COUNTRIES:
            token.misc["COUNTRY"] = "YES"
            token.upos = "PROPN"

# Print to standard out which can then be redirected.
conllu.write_corpus(corpus, sys.stdout)
