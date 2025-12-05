Custom Token Schemas
===================================

Version 4.0 allows you to define custom token formats to parse and serialize beyond the base CoNLL-U format.

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

The compilation happens once when creating a Format instance, so reuse Format instances for best performance.

.. _schema: pyconll/schema.html
.. _format: pyconll/format.html
