Saving Data
===========

``MATS`` provides a very flexible module for saving data.

``ArchiveManager``
------------------

The builtin ``ArchiveManager`` is the default class built for saving data.  The ``ArchiveManager``
really implements one method, ``save()``.  The ``save()`` method accepts a ``dict`` as the parameter
which contains key: value pairs containing the results of a single test execution.

Custom ArchiveManager Implementations
-------------------------------------

.. todo::

   Describe how to create a custom class for the archive manager.
