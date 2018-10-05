#!/usr/bin/env python

#
# Add a singleton feature to the misc column of all tokens of a certain form.
#
# Format
#   add_misc_features.py filename > transform.conll
#

import argparse

import pyconll

parser = argparse.ArgumentParser()
parser.add_argument('filename', help='The name of the file to transform')
args = parser.parse_args()

corpus = pyconll.load_from_file(args.filename)
for sentence in corpus:
    for token in sentence:
        if token.lemma == 'dog' and token.upos == 'VERB':
            # Note: This means that 'Polysemous' will be present as a singleton
            # in the token line. To remove 'Polysemous' from the token's
            # features, call del token.misc['Polysemous']
            token.misc['Polysemous'] = None

# Print to standard out which can then be redirected.
print(corpus.conll())
