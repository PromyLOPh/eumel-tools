EUMEL-python
============

Tools for dealing with EUMEL_ datastructures and files, mostly written in Python.

.. _EUMEL: https://6xq.net/eumel/

``elan.py``
    is a lexer for pygments and used to highlight the packages found
    `here <https://6xq.net/eumel/src/>`__.
``extractAll.sh``
    bulk-extracts all archive disk images whose paths are read from stdin. It
    also converts text dataspaces to text files usable with modern computers.

    Calls ``convertCharset.py``, ``convertFileDs.py``, ``extractArchive.py``
    and ``linearizeDisk.py``.
