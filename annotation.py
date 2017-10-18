import re

from collections import defaultdict
from recordclass import recordclass

AnnotationLineInternal = recordclass('AnnotationLineInternal', ['type', 'dep', 'line_nums', 'ann'])
class AnnotationLine(AnnotationLineInternal):
    def is_annotated(self):
        return self.ann is not None

    def correct_in_corpus(self):
        return self.ann == 'y'

    def __str__(self):
        if self.ann:
            output = '{} | {}, {} at {} {}'
        else:
            output = '{} | {}, {} at {}'

        return output.format(self.type, self.dep[0], self.dep[1],
                             self.line_nums, self.ann)

# TODO: Rename this to be more representative of the class.
class Annotation(object):
    # A line in the annotation file is a line that can be annotated.
    # Basically this lines that are not headers, lemma pairs or
    # newlines.
    LINE_REGEX = '^\t(context|nil) \| (.+) at \((\d+), (\d+)\)(\s+(y|n)\s*)?\n$'
    EXPLICIT_LINE_REGEX = '^\t(context|nil) \| (.+) at \((\d+), (\d+)\)(\s+(y|n)\s*)?\n$'
    CONTEXT_INCONS = 'context'
    NIL_INCONS = 'nil'

    def __init__(self):
        self.annotations = defaultdict(list)
        self.lemmas = 0
        self.size = 0
        self.nils = 0
        self.contexts = 0

    def from_filename(self, filename):
        with open(filename, 'r') as f:
            cur_header = None
            cur_lemmas = None

            for line in f:
                m = re.match(Annotation.LINE_REGEX, line)
                if m:
                    dep_t = tuple(m.group(2).split(', '))
                    ls_n = (int(m.group(3)), int(m.group(4)))

                    line_ann = AnnotationLine(m.group(1), dep_t, ls_n, m.group(5))
                    self.annotations[cur_lemmas].append(line_ann)

                    if m.group(1) == Annotation.CONTEXT_INCONS:
                        self.contexts += 1
                    elif m.group(1) == Annotation.NIL_INCONS:
                        self.nils += 1
                    self.size += 1
                elif line not in ['\n', '\r\n']:
                    # This line is starting off a pair of lemmas, so split
                    # it into the two lemmas, ignoring the '\n' in the
                    # second lemma.
                    comma = line.index(', ')
                    first_lemma = line[:comma]
                    second_lemma = line[comma + 2:-1]

                    cur_lemmas = frozenset((first_lemma, second_lemma))
                    self.lemmas += 1

    # Check if this file has a desired line. Provide the set of lemmas as
    # strings and also the provide the AnnotationLine object that represents the
    # desired line. Note that this does not take annotation into account, such
    # as 'y' or 'n'.
    def has_line(self, lemmas, l):
        return self._find_line(lemmas, l) is not None

    # Set the given line to have the given annotation. lemmas is a set of the
    # desired lemmas and l is the AnnotationLine object that represents the
    # desired line.
    def set_line(self, lemmas, l, ann):
        l = self._find_line(lemmas, l)
        if l:
            l.ann = ann

    def _find_line(self, lemmas, l):
        for line in self.annotations[lemmas]:
            if line.type == l.type and line.dep == l.dep and line.line_nums == l.line_nums:
                return line

        return None

    def output(self, filename):
        with open(filename, 'w') as f:
            for lemmas, occurences in self.annotations.items():
                if len(occurences) > 0:
                    if len(lemmas) > 1:
                        f.write(', '.join(lemmas) + '\n')
                    else:
                        l, = lemmas
                        f.write('{}, {}\n'.format(l, l))

                    for o in occurences:
                        dep_s = ', '.join(o.dep)
                        if o.is_annotated():
                            line = '\t{} | {} at {} {}\n'.format(o.type, dep_s, o.line_nums, o.ann)
                        else:
                            line = '\t{} | {} at {}\n'.format(o.type, dep_s, o.line_nums)

                        f.write(line)

                    f.write('\n')
