exception
===================================

Custom exceptions for pyconll. These errors are ``ParseError``, ``FormatError``, and ``SchemaError``.

A ``ParseError`` occurs when the source input to a CoNLL component is invalid. A ``FormatError`` occurs when the internal state of the component is invalid, and the component cannot be output to a CoNLL string. A ``SchemaError`` occurs when the Token schema provided to a Format instance is invalid and cannot be compiled.


API
----------------------------------
.. automodule:: pyconll.exception
    :members:
    :special-members:
    :exclude-members: __dict__, __weakref__
