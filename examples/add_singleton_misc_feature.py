#
# Add a singleton feature to the misc column of all tokens of a certain form.
#
# Format
#   add_singleton_misc_feature.py filename > transform.conll
#

import argparse
import sys

from pyconll.conllu import Format as conllu

parser = argparse.ArgumentParser()
parser.add_argument('filename', help='The name of the file to transform')
args = parser.parse_args()

corpus = conllu.load_from_file(args.filename)
for sentence in corpus:
    for token in sentence.tokens:
        if token.lemma.lower() == 'dog' and token.upos == 'VERB':
            # Note: This means that 'Polysemous' will be present as a singleton
            # in the token line. To remove 'Polysemous' from the token's
            # features, call del token.misc['Polysemous']
            token.misc['Polysemous'] = None

# Print to standard out which can then be redirected.
conllu.write_corpus(corpus, sys.stdout)
