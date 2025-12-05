schema
===================================

The ``schema`` module defines the ``@tokenspec`` decorator and field descriptors for defining custom token types. This is the foundation of pyconll's flexible format system.

@tokenspec Decorator
----------------------------------

The ``@tokenspec`` decorator is used to mark a class as a token specification that can be used with the ``Format`` system. To create a custom token schema:

1. Define a class with typed fields using Python type hints.
2. Decorate the class with ``@tokenspec``.
3. Optionally use field descriptors for more complex serialization definitions.
4. Add any necessary extra behavior to your class that can use the deserialized values.

The field order in your class definition determines the column order in the serialized output.

Basic Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from pyconll.schema import tokenspec

    @tokenspec
    class SimpleToken:
        id: int
        form: str
        lemma: str
        pos: str

    # This defines a 4-column format where columns are parsed as:
    # int, str, str, str

Supported Field Types
----------------------------------

Basic Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
These types can be used directly without field descriptors:

- ``str`` - String column
- ``int`` - Integer column
- ``float`` - Float column

Field Descriptors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For more complex column types, use field descriptors. The following terminology or points may be helpful for understanding the API.

* The ``empty_marker`` parameters correspond to what text will exclusively map to the empty value for the field's native type. For a nullable, that is ``None``, for a ``unique_array`` it would be an empty set, etc...
* Each field descriptor also takes a nested mapper. This allows for composition of multiple descriptors. The mapper can be another descriptor, or one of the supported primitive types.

nullable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents optional values with an empty marker.

.. code:: python

    from pyconll.schema import tokenspec, nullable, field

    @tokenspec
    class Token:
        id: str
        lemma: Optional[str] = field(nullable(str, "_"))
        # "_" represents None/null, otherwise parsed as string

array
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents lists with a delimiter.

.. code:: python

    from pyconll.schema import tokenspec, array, field

    @tokenspec
    class Token:
        features: list[str] = field(array(str, "|", "_"))
        # Values separated by "|", "_" for empty list

unique_array
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents sets (unordered, unique values) with optional ordering for serialization.

.. code:: python

    from pyconll.schema import tokenspec, unique_array, field

    @tokenspec
    class Token:
        tags: set[str] = field(unique_array(str, "|", "_", str.lower))
        # Set of strings, serialized in order by lowercase value

fixed_array
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents tuples (fixed-length sequences).

.. code:: python

    from pyconll.schema import tokenspec, fixed_array, field

    @tokenspec
    class Token:
        tup: tuple[str, ...] = field(fixed_array(str, "|", "_"))

mapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents dictionaries with key-value pairs.

.. code:: python

    from pyconll.schema import tokenspec, mapping, unique_array, field

    @tokenspec
    class Token:
        # CoNLL-U feats: Gender=Fem|Number=Sing
        feats: dict[str, set[str]] = field(
            mapping(
                str,                           # Key mapper
                unique_array(str, ","),        # Value mapper (set of strings)
                "|",                           # Pair delimiter
                "=",                           # Key-value delimiter
                "_",                           # Empty marker
                lambda p: p[0].lower()         # Ordering key
            )
        )

mapping_ext
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents dictionaries that can have singleton keys (keys without values). This is useful for formats like CoNLL-U's MISC field where you can have both ``Key=Value`` and standalone ``Key`` entries.

.. code:: python

    from pyconll.schema import tokenspec, mapping_ext, unique_array, field

    @tokenspec
    class Token:
        # Misc field: SpaceAfter=No|Translit=example|SpellId
        # SpellId is a singleton (no value)
        misc: dict[str, Optional[set[str]]] = field(
            mapping_ext(
                str,                           # Key mapper
                unique_array(str, ","),        # Value mapper (set of strings)
                None,                          # Singleton marker (value when no = present)
                "|",                           # Pair delimiter
                "=",                           # Key-value delimiter
                "_",                           # Empty marker
                lambda p: p[0].lower()         # Ordering key
            )
        )

varcols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents variable number of column (including an empty width). It does not have to be the last field, but only one column can use it for a given class.

.. code:: python

    from pyconll.schema import tokenspec, varcols, field

    @tokenspec
    class Token:
        id: int
        form: str
        extra: list[str] = field(varcols(str))
        # All remaining columns parsed as strings

via
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Custom (de)serialization functions.

.. code:: python

    from pyconll.schema import tokenspec, via, field
    from datetime import datetime

    def parse_date(s: str) -> datetime:
        return datetime.fromisoformat(s)

    def serialize_date(d: datetime) -> str:
        return d.isoformat()

    @tokenspec
    class Token:
        timestamp: datetime = field(via(parse_date, serialize_date))

Complete Example: CoNLL-U
----------------------------------

The CoNLL-U Token schema demonstrates many of these features in concert:

.. code:: python

    from pyconll.schema import (
        tokenspec, nullable, mapping, mapping_ext, unique_array,
        fixed_array, field
    )
    from typing import Optional

    @tokenspec
    class Token:
        id: str
        form: Optional[str] = field(nullable(str, "_"))
        lemma: Optional[str] = field(nullable(str, "_"))
        upos: Optional[str] = field(nullable(str, "_"))
        xpos: Optional[str] = field(nullable(str, "_"))

        # Features: Gender=Fem|Number=Sing
        feats: dict[str, set[str]] = field(
            mapping(
                str,
                unique_array(str, ",", "", str.lower),
                "|",
                "=",
                "_",
                lambda p: p[0].lower()
            )
        )

        head: Optional[str] = field(nullable(str, "_"))
        deprel: Optional[str] = field(nullable(str, "_"))

        # Enhanced dependencies: 4:nsubj|8:nmod:tmod
        deps: dict[str, tuple[str, ...]] = field(
            mapping(
                str,
                fixed_array(str, ":"),
                "|",
                ":",
                "_",
                lambda p: p[0]
            )
        )

        # Misc: SpaceAfter=No|Translit=example or singleton keys like SpellId
        misc: dict[str, Optional[set[str]]] = field(
            mapping_ext(
                str,
                unique_array(str, ",", "", str.lower),
                None,  # Singleton marker for keys without values
                "|",
                "=",
                "_",
                lambda p: p[0].lower()
            )
        )

Token Lifecycle Hooks
----------------------------------

The ``@tokenspec`` decorator supports a ``__post_init__`` method that runs custom logic after token initialization:

.. code:: python

    from pyconll.schema import tokenspec

    @tokenspec
    class Token:
        id: int
        form: str
        processed: bool = False

        def __post_init__(self) -> None:
            # This runs after all fields are set during parsing
            self.processed = True

    # After parsing, token.processed will be True

This is useful for:
- Computing derived fields
- Validation
- Normalization
- Special handling (e.g., CoNLL-U's form/lemma underscore logic)

Advanced: Dynamic Field Descriptors
----------------------------------

While the typical approach is to use ``field()`` as class attributes, you can also provide field descriptors dynamically via the ``field_descriptors`` parameter in the ``Format`` constructor. This is useful for:

- Switching between different descriptor implementations at runtime
- Sharing token classes across different formats
- Advanced performance tuning

.. code:: python

    from pyconll.schema import tokenspec, nullable, FieldDescriptor
    from pyconll.format import Format

    @tokenspec
    class Token:
        id: str
        form: str
        lemma: str
        upos: str

    # Define descriptors separately
    field_descriptors: dict[str, Optional[FieldDescriptor]] = {
        'id': None,  # None for primitive types (int, float, str)
        'form': nullable(str, "_"),
        'lemma': nullable(str, "_"),
        'upos': nullable(str, "_"),
    }

    # Pass to Format constructor
    my_format = Format(Token, Sentence[Token], field_descriptors=field_descriptors)

When both class attributes and ``field_descriptors`` are provided, ``field_descriptors`` takes precedence. This allows you to override the class-level descriptors at Format creation time.

SentenceBase Interface
----------------------------------

The ``SentenceBase`` is an abstract interface that defines how Sentence implementations work with the Format system. Any Sentence type used with Format must implement this interface.

Required Methods and Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from pyconll.schema import SentenceBase
    from typing import OrderedDict

    class MySentence(SentenceBase[MyToken]):
        def __init__(self) -> None:
            # Must have a no-argument constructor
            self._meta: OrderedDict[str, Optional[str]] = OrderedDict()
            self._tokens: list[MyToken] = []

        @property
        def meta(self) -> MutableMapping[str, Optional[str]]:
            return self._meta

        @meta.setter
        def meta(self, value: MutableMapping[str, Optional[str]]) -> None:
            self._meta = value

        @property
        def tokens(self) -> MutableSequence[MyToken]:
            return self._tokens

        @tokens.setter
        def tokens(self, value: MutableSequence[MyToken]) -> None:
            self._tokens = value

        def __accept_meta__(self, key: str, value: Optional[str]) -> None:
            # Called during parsing for each metadata pair
            self.meta[key] = value

        def __accept_token__(self, t: MyToken) -> None:
            # Called during parsing for each token
            self.tokens.append(t)

        def __finalize__(self) -> None:
            # Called when sentence parsing is complete
            pass

The lifecycle methods (``__accept_meta__``, ``__accept_token__``, ``__finalize__``) allow custom sentence implementations to process data incrementally during parsing, enabling streaming scenarios and custom initialization logic.

API
----------------------------------
.. automodule:: pyconll.schema
    :members:
    :exclude-members: __dict__, __weakref__
