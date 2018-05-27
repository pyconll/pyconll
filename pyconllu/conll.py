from collections import defaultdict
import re

from tree import *

# TODO: API for TreeBank is getting a little messy and confusing. Try to clean up.
class TreeBank(object):
    # Seed a TreeBank object with a filename so that a generator type object can
    # be created. Rather than reading in the whole file and storing it in memory
    # before you iterate through. None of the sentences are stored afterward in
    # the TreeBank.
    def genr(self, filename):
        # TODO: Consolidate code between this and from_filename.
        with open(filename, 'r') as f:
            lines = []
            sent_start = 1
            for i, line in enumerate(f):
                stripped = line.strip()

                # If the line is not blank then add it to the running
                # list of lines for the current sentence.
                if stripped:
                    lines.append(stripped)
                else:
                    # Otherwise, the line is blank and the end of this
                    # sentence has been reached. So combine the lines
                    # found for this sentence and create Sentence
                    # object.
                    annotation = '\n'.join(lines)
                    yield Sentence(annotation, sent_start)
                    sent_start = i + 2
                    del lines[:]

    def from_filename(self, filename):
        self.sentences = []

        with open(filename, 'r') as f:
            lines = []
            sent_start = 1
            for i, line in enumerate(f):
                stripped = line.strip()

                # If the line is not blank then add it to the running
                # list of lines for the current sentence.
                if stripped:
                    lines.append(stripped)
                else:
                    # Otherwise, the line is blank and the end of this
                    # sentence has been reached. So combine the lines
                    # found for this sentence and create Sentence
                    # object.
                    annotation = '\n'.join(lines)
                    self.sentences.append(Sentence(annotation, sent_start))
                    sent_start = i + 2
                    del lines[:]

    def from_string(self, string):
        self.sentences = []
        lines = string.splitlines();

        start = 0
        idx = 0
        while start < len(lines):
            line = lines[idx].strip()

            if not line:
                annotation = '\n'.join(lines[start:idx])
                self.sentences.append(Sentence(annotation, start + 1))

                start = idx + 1

            idx += 1


    def output(self, filename):
        pass

    def __iter__(self):
        for sentence in self.sentences:
            yield sentence

    def __getitem__(self, key):
        return self.sentences[key]

class Sentence(object):
    COMMENT_MARKER = '#'
    SENTENCE_ID_REGEX = COMMENT_MARKER + ' sent_id = ([a-z]{2}-ud-(dev|train|test)_\d+)'
    CONTRACTION_REGEX = '^\d+-\d+'
    SENTENCE_TEXT_MARKER = '='

    def __init__(self, annotation, line_num=-1):
        self.line_num = line_num
        self.words = []
        self.lines = annotation.splitlines()

        id_match = re.match(Sentence.SENTENCE_ID_REGEX, self.lines[0])
        if id_match:
            self.id = id_match.group(1)
        else:
            self.id = None

        self.indexes = {}
        word_index = 0
        for i, line in enumerate(self.lines):
            if self._is_word_line(line):
                word_line = -1 if line_num == -1 else self.line_num + i
                w = Word(line, word_line)
                self.indexes[w.index] = word_index
                self.words.append(w)

                word_index += 1

        # This is to handle the cases where the format is different
        # from the French corpus.
        # TODO: Comment that for accurate sentence text need space after
        # ':'
        try:
            marker_index = self.lines[1].index(Sentence.SENTENCE_TEXT_MARKER)
            self.text = self.lines[1][marker_index + 2:]
        except:
            self.text = ""

    def next(self, index):
        next_index = min(self.indexes[index] + 1, len(self.words) - 1)
        return self.words[next_index]

    def _is_word_line(self, line):
        return line[0] != Sentence.COMMENT_MARKER and not re.match(Sentence.CONTRACTION_REGEX, line)

    # Only accepts strings and slice objects for getitem. This is because there
    # are decimal indexes in UD v2. So this is best handled by a string which
    # is mapped to an underlying integer for the word list.
    def __getitem__(self, key):
        if isinstance(key, slice):
            start = self.indexes[key.start]
            stop = self.indexes[key.stop]
            return self.words[start : stop]
        elif isinstance(key, str):
            return self.words[self.indexes[key]]
        elif isinstance(key, int):
            return self.words[key]

    def __len__(self):
        return len(self.words)

# A navigable tree created from a provided Sentence object. The
# sentence's root is the root of this tree. The root's dependents are
# then the children of the root node and so on. The SentenceTree also
# actually extends Tree, so look to that for more info, this is just a
# wrapper around the construction of a tree data structure from a
# sentence object.
class SentenceTree(Tree):
    def __init__(self, sentence):
        self.sentence = sentence
        deps = defaultdict(list)
        for word in self.sentence:
            deps[word.dep_index].append(word)

        root = deps['0'][0]
        super(SentenceTree, self).__init__(root)

        self._construct_tree(self, deps)

    def _construct_tree(self, t, deps):
        next_children = deps[t.node.index]

        for child in next_children:
            next_t = Tree(child)
            self._construct_tree(next_t, deps)
            t.add_children(next_t)

class Word(object):
    FIELD_DELIMITER = '\t'
    FEATURE_DELIMITER = '|'

    def __init__(self, annotation, line_num=-1):
        self.line_num = line_num
        fields = annotation.split(Word.FIELD_DELIMITER)

        self.index = fields[0]
        self.phon = fields[1]
        self.lemma = fields[2]
        self.pos = fields[3]
        self.features = fields[5]
        self.dep_index = fields[6]
        self.dep = fields[7]
        self.deps = fields[8]
        self.misc = fields[9]

    def __str__(self):
        return self.phon

    def __repr__(self):
        items = [self.index, self.phon, self.lemma, self.pos, self.features,
                 self.dep_index, self.dep, self.deps, self.misc]
        return Word.FIELD_DELIMITER.join(items)
