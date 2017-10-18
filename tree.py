from itertools import chain, imap

class Tree(object):
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def add_children(self, *children):
        for child in children:
            child.parent = self
            self.children.append(child)

    # Returns the subtrees whose root nodes equal the provided node.
    # If there are no such trees than an empty list is returned.
    def find_trees_by_node(self, callback, expected):
        trees = []

        if callback(self.node) == expected:
            trees.append(self)
        else:
            for child in self.children:
                child_matches = child.find_trees_by_node(callback, expected)
                if child_matches:
                    trees += child_matches

        return trees

    # Checks if the given node is in the tree and returns a boolean
    # response. To be used with `in` operator.
    def __contains__(self, value):
        contains = self.node == value
        if not contains:
            for child in self.children:
                contains = value in child

                if contains:
                    break

        return contains

    def __iter__(self):
        yield self
        # TODO: Look into how this works
        for child in chain(*imap(iter, self.children)):
            yield child

    def size(self):
        s = 0

        if self.node:
            s += 1

        for child in self.children:
            s += child.size()

        return s
