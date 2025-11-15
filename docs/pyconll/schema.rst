schema
===================================

The ``schema`` module defines the ``TokenSchema`` protocol and field descriptors for defining custom token types. This is the foundation of pyconll's flexible format system.

TokenSchema Protocol
----------------------------------

``TokenSchema`` is a protocol that any token class must satisfy to be used with the ``Format`` system. To create a custom token schema:

1. Create a Protocol by subclassing the ``TokenSchema``.
2. Add typed fields using Python type hints. These fields are defined at the class level.
3. Optionally use field descriptors for more complex serialization definitions.
4. Add any necessary extra behavior to your class that can use the deserialized values.

The field order in your class definition determines the column order in the serialized output.

Basic Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from pyconll.schema import TokenSchema

    class SimpleToken(TokenSchema):
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

    from pyconll.schema import nullable, field

    class Token(TokenSchema):
        id: str
        lemma: Optional[str] = field(nullable(str, "_"))
        # "_" represents None/null, otherwise parsed as string

array
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents lists with a delimiter.

.. code:: python

    from pyconll.schema import array, field

    class Token(TokenSchema):
        features: list[str] = field(array(str, "|", "_"))
        # Values separated by "|", "_" for empty list

unique_array
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents sets (unordered, unique values) with optional ordering for serialization.

.. code:: python

    from pyconll.schema import unique_array, field

    class Token(TokenSchema):
        tags: set[str] = field(unique_array(str, "|", "_", str.lower))
        # Set of strings, serialized in order by lowercase value

fixed_array
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents tuples (fixed-length sequences).

.. code:: python

    from pyconll.schema import fixed_array, field

    class Token(TokenSchema):
        tup: tuple[str, ...] = field(fixed_array(str, "|", "_"))

mapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents dictionaries with key-value pairs.

.. code:: python

    from pyconll.schema import mapping, unique_array, field

    class Token(TokenSchema):
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

varcols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Represents variable number of column (including an empty width). It does not have to be the last field, but only one column can use it for a given class.

.. code:: python

    from pyconll.schema import varcols, field

    class Token(TokenSchema):
        id: int
        form: str
        extra: list[str] = field(varcols(str))
        # All remaining columns parsed as strings

via
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Custom (de)serialization functions.

.. code:: python

    from pyconll.schema import via, field
    from datetime import datetime

    def parse_date(s: str) -> datetime:
        return datetime.fromisoformat(s)

    def serialize_date(d: datetime) -> str:
        return d.isoformat()

    class Token(TokenSchema):
        timestamp: datetime = field(via(parse_date, serialize_date))

Complete Example: CoNLL-U
----------------------------------

The CoNLL-U Token schema demonstrates many of these features in concert:

.. code:: python

    from pyconll.schema import TokenSchema, nullable, mapping, unique_array, field
    from typing import Optional

    class Token(TokenSchema):
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

        # Enhanced dependencies
        deps: dict[str, tuple[str, str, str, str]] = field(
            mapping(
                str,
                fixed_array(str, ":", ""),
                "|",
                ":",
                "_",
                lambda p: (p[0], *p[1]),
                use_compact_pair=True
            )
        )

        # Misc: SpaceAfter=No|Translit=example
        misc: dict[str, Optional[set[str]]] = field(
            mapping(
                str,
                nullable(unique_array(str, ",", "", str.lower), ""),
                "|",
                "=",
                "_",
                lambda p: p[0].lower(),
                use_compact_pair=True
            )
        )

Token Lifecycle Hooks
----------------------------------

The ``@token_lifecycle`` decorator allows you to run custom logic after token initialization:

.. code:: python

    from pyconll.schema import TokenSchema, token_lifecycle

    @codegen(post_init=lambda self: setattr(self, 'processed', True))
    class Token(TokenSchema):
        id: int
        form: str
        processed: bool = False

    # After parsing, token.processed will be True, but there is no method
    # on the interface which pollutes the data model.

This is useful for:
- Computing derived fields
- Validation
- Normalization

API
----------------------------------
.. automodule:: pyconll.schema
    :members:
    :exclude-members: __dict__, __weakref__
