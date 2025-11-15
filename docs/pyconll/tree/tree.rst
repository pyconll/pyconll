tree
===================================

``Tree`` is a simple, generic tree data structure for representing hierarchical relationships between tokens (such as dependency trees). A ``Tree`` can have multiple children and one parent.

Overview
----------------------------------

The tree module provides:

- ``Tree[T]`` - A generic tree node containing data of type T
- ``from_tokens()`` - A function to build trees from sequences of tokens
- For CoNLL-U specifically, use ``tree_from_tokens()`` from the ``pyconll.conllu`` module

Structure
----------------------------------

A ``Tree`` has the following key components:

- ``data: T`` - The data stored at this node (e.g., a Token)
- ``parent: Optional[Tree[T]]`` - The parent node (None for root)
- ``__getitem__(i)`` - Access children by index
- ``__iter__()`` - Iterate over children
- ``__len__()`` - Number of children

Creating Trees
----------------------------------

Generic Tree Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``tree.from_tokens()`` to create trees from any sequence of tokens:

.. code:: python

    from pyconll.tree import from_tokens

    tree = from_tokens(
        tokens=my_tokens,
        starting_id='0',                        # Root parent ID
        to_id=lambda t: t.id,                   # Extract token ID
        to_head=lambda t: t.head,               # Extract parent ID
        skip=lambda t: '-' in t.id              # Skip multiword tokens
    )

CoNLL-U Tree Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For CoNLL-U tokens, use the convenience function:

.. code:: python

    from pyconll.conllu import conllu, tree_from_tokens

    sentences = conllu.load_from_file('train.conllu')

    for sentence in sentences:
        tree = tree_from_tokens(sentence.tokens)

        # Tree root is the token with head="0"
        root_token = tree.data
        print(f"Root: {root_token.form}")

        # Iterate over dependents
        for child_tree in tree:
            child_token = child_tree.data
            print(f"  Dependent: {child_token.form}")

Traversing Trees
----------------------------------

.. code:: python

    from pyconll.conllu import conllu, tree_from_tokens

    sentences = conllu.load_from_file('train.conllu')
    tree = tree_from_tokens(sentences[0].tokens)

    # Access root data
    root = tree.data
    print(f"Root word: {root.form}, POS: {root.upos}")

    # Iterate over direct children
    for child_tree in tree:
        child = child_tree.data
        print(f"Dependent: {child.form} ({child.deprel})")

        # Recursively process subtree
        for grandchild_tree in child_tree:
            grandchild = grandchild_tree.data
            print(f"  Grandchild: {grandchild.form}")

    # Access children by index
    if len(tree) > 0:
        first_child = tree[0]
        print(f"First dependent: {first_child.data.form}")

Example: Finding Non-Projective Dependencies
----------------------------------

.. code:: python

    from pyconll.conllu import conllu, tree_from_tokens

    def has_nonprojective(tree, start=None, end=None):
        """Check if tree has non-projective dependencies."""
        if start is None:
            # Get token IDs for span calculation
            token_ids = set()
            collect_ids(tree, token_ids)
            start = min(int(id) for id in token_ids if id.isdigit())
            end = max(int(id) for id in token_ids if id.isdigit())

        for child in tree:
            child_id = int(child.data.id) if child.data.id.isdigit() else 0
            if child_id < start or child_id > end:
                return True
            if has_nonprojective(child, start, end):
                return True
        return False

    sentences = conllu.load_from_file('train.conllu')
    for sentence in sentences:
        tree = tree_from_tokens(sentence.tokens)
        if has_nonprojective(tree):
            print(f"Non-projective: {sentence.meta.get('sent_id')}")

Version 4.0 Changes
----------------------------------

.. note::
    **Version 4.0** changed how trees are created:

    - **Before:** ``tree = sentence.to_tree()``
    - **After:** ``tree = tree_from_tokens(sentence.tokens)`` (from ``pyconll.conllu``)

    Or use the generic ``tree.from_tokens()`` for custom token types.

API
----------------------------------
.. automodule:: pyconll.tree
    :members:
    :special-members:
    :exclude-members: __dict__, __weakref__
