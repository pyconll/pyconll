Migration Guide: Version 3.x to 4.0
===================================

Version 4.0 introduces significant architectural improvements to pyconll. This guide helps you migrate from earlier versions to 4.0.

Overview of Changes
----------------------------------

Version 4.0 brings major improvements:

- **Flexible schema system** for custom tabular formats
- **Improved performance** through compiled parsers/serializers
- **Simplified object model** with standard Python collections
- **Better type safety** with generics

Quick Migration Checklist
----------------------------------

1. Update imports from ``import pyconll`` to ``from pyconll.conllu import conllu``. All methods that were previously exposed on ``pyconll`` can now be found on the ``conllu`` instance.
2. Change return type expectations from ``Conll`` to ``list[Sentence]``
3. Update token access from ``sentence[token_index]`` to ``sentence.tokens``
4. Update metadata access from ``sentence.id`` to ``sentence.meta['sent_id']``
5. Change tree creation from ``sentence.to_tree()`` to ``pyconll.conllu.tree_from_tokens(sentence.tokens)``
6. Update serialization from ``.conll()`` methods to ``WriteFormat`` methods

Detailed Migration Steps
----------------------------------

1. Import Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before:**

.. code:: python

    import pyconll

**After:**

.. code:: python

    from pyconll.conllu import conllu

The module structure has changed to support multiple formats. For CoNLL-U, use the ``conllu`` module.

2. Loading Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before:**

.. code:: python

    import pyconll

    # Load into memory
    corpus = pyconll.load_from_file('train.conllu')  # Returns Conll object

    # Stream
    for sentence in pyconll.iter_from_file('train.conllu'):
        pass

**After:**

.. code:: python

    from pyconll.conllu import conllu

    # Load into memory
    corpus = conllu.load_from_file('train.conllu')  # Returns list[Sentence]

    # Stream
    for sentence in conllu.iter_from_file('train.conllu'):
        pass

The ``Conll`` wrapper object is gone. Loading methods now return standard Python lists.

3. Iterating Over Corpus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before:**

.. code:: python

    corpus = pyconll.load_from_file('train.conllu')

    for sentence in corpus:  # Conll implements MutableSequence
        for token in sentence:  # Sentence is iterable over tokens
            print(token.form)

**After:**

.. code:: python

    corpus = conllu.load_from_file('train.conllu')

    for sentence in corpus:  # Standard list iteration
        for token in sentence.tokens:  # Access .tokens attribute
            print(token.form)

The main difference is accessing ``sentence.tokens`` instead of iterating directly over ``sentence``.

4. Accessing Tokens by ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before:**

.. code:: python

    for sentence in corpus:
        for token in sentence:
            if token.head != '0':
                head_token = sentence[token.head]  # Direct ID lookup
                print(f"{token.form} -> {head_token.form}")

**After:**

.. code:: python

    for sentence in corpus:
        # Build token index
        token_by_id = {t.id: t for t in sentence.tokens}

        for token in sentence.tokens:
            if token.head != '0':
                head_token = token_by_id.get(token.head)
                if head_token:
                    print(f"{token.form} -> {head_token.form}")

Sentences no longer support indexing by token ID. Build your own index if needed.

5. Accessing Sentence Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before:**

.. code:: python

    for sentence in corpus:
        print(sentence.id)    # Direct property access
        print(sentence.text)

        # Or via meta methods
        sent_id = sentence.meta_value('sent_id')

**After:**

.. code:: python

    for sentence in corpus:
        print(sentence.meta['sent_id'])  # Dictionary access
        print(sentence.meta['text'])

        # Add metadata
        sentence.meta['custom'] = 'value'

        # Singleton metadata
        sentence.meta['newpar'] = None

Metadata is now accessed as a standard OrderedDict.

6. Creating Dependency Trees
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before:**

.. code:: python

    for sentence in corpus:
        tree = sentence.to_tree()  # Method on Sentence
        root = tree.data
        for child in tree:
            print(child.data.form)

**After:**

.. code:: python

    from pyconll.conllu import conllu, tree_from_tokens

    corpus = conllu.load_from_file('train.conllu')

    for sentence in corpus:
        tree = tree_from_tokens(sentence.tokens)  # Standalone function
        root = tree.data
        for child in tree:
            print(child.data.form)

Tree creation is now a separate function rather than a method on Sentence.

7. Serialization (Writing Output)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before:**

.. code:: python

    # Serialize to string
    conll_string = corpus.conll()
    sentence_string = sentence.conll()
    token_string = token.conll()

    # Write to file
    with open('output.conllu', 'w') as f:
        corpus.write(f)

**After:**

.. code:: python

    from pyconll.conllu import conllu

    # Serialize individual items
    sentence_string = conllu.serialize_sentence(sentence)
    token_string = conllu.serialize_token(token)

    # Write to file (recommended)
    with open('output.conllu', 'w') as f:
        conllu.write_corpus(corpus, f)

Serialization is now handled by the Format instance rather than methods on objects.

Complete Migration Example
----------------------------------

**Before:**

.. code:: python

    import pyconll

    # Load
    train = pyconll.load_from_file('./ud/train.conllu')

    # Process
    for sentence in train:
        # Access metadata
        print(f"Sentence: {sentence.id}")

        # Build tree
        tree = sentence.to_tree()

        # Process tokens
        for token in sentence:
            if token.upos == 'VERB':
                # Look up head
                if token.head != '0':
                    head = sentence[token.head]
                    print(f"{token.form} -> {head.form}")

    # Write output
    with open('output.conllu', 'w') as f:
        train.write(f)

**After:**

.. code:: python

    from pyconll.conllu import conllu, tree_from_tokens

    # Load
    train = conllu.load_from_file('./ud/train.conllu')

    # Process
    for sentence in train:
        # Access metadata
        print(f"Sentence: {sentence.meta.get('sent_id')}")

        # Build tree
        tree = tree_from_tokens(sentence.tokens)

        # Build token index for lookups
        token_by_id = {t.id: t for t in sentence.tokens}

        # Process tokens
        for token in sentence.tokens:
            if token.upos == 'VERB':
                # Look up head
                if token.head != '0':
                    head = token_by_id.get(token.head)
                    if head:
                        print(f"{token.form} -> {head.form}")

    # Write output
    with open('output.conllu', 'w') as f:
        conllu.write_corpus(train, f)

New Features in 4.0
----------------------------------

Custom Token Schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Version 4.0 allows you to define custom token formats:

.. code:: python

    from pyconll.format import Format
    from pyconll.schema import tokenspec, nullable, unique_array, field, SentenceBase
    from pyconll.shared import Sentence
    from typing import Optional

    @tokenspec
    class CoNLLX:
        id: int
        form: str
        lemma: str
        cpostag: str
        postag: str
        feats: set[str] = field(unique_array(str, "|", "_"))
        head: int
        deprel: str
        phead: Optional[int] = field(nullable(int, "_"))
        pdeprel: Optional[str] = field(nullable(str, "_"))

    conllx = Format(CoNLLX, Sentence[CoNLLX])

    # Use it
    sentences = conllx.load_from_file('data.conllx')

See the schema_ and format_ documentation for more details.

Performance Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Version 4.0 uses compiled parsers and serializers:

- Faster parsing (25-35% improvement)
- Lower memory footprint
- Better type safety

The compilation happens once when creating a Format instance, so reuse Format instances for best performance.

Troubleshooting
----------------------------------

Common Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**AttributeError: 'Sentence' object has no attribute 'id'**

Use ``sentence.meta.get('sent_id')`` instead of ``sentence.id``.

**TypeError: 'Sentence' object is not subscriptable**

Sentences no longer support ``sentence[token_id]``. Build an index:

.. code:: python

    token_by_id = {t.id: t for t in sentence.tokens}
    token = token_by_id.get(token_id)

**AttributeError: 'list' object has no attribute 'write'**

The ``Conll`` object is gone. Use the Format instance:

.. code:: python

    with open('output.conllu', 'w') as f:
        conllu.write_corpus(sentences, f)

**AttributeError: 'Token' object has no attribute 'conll'**

Use the Format instance:

.. code:: python

    token_string = conllu.serialize_token(token)

Getting Help
----------------------------------

If you encounter issues during migration:

- Check the updated documentation_
- Review the examples_ in the repository
- Ask questions on GitHub_

.. _schema: pyconll/schema.html
.. _format: pyconll/format.html
.. _documentation: index.html
.. _examples: https://github.com/pyconll/pyconll/tree/master/examples
.. _GitHub: https://github.com/pyconll/pyconll/issues
