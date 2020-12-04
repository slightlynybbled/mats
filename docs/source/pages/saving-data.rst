.. _saving-data-label:

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

To create your own custom implementation that will save your data, you must:

1. Implement a new class which contains a ``save()`` method which accepts a single ``dict`` as \
   its parameter.
2. Create an instance of your new custom class:

.. code-block:: python

    mam = MyArchiveManager()

3. Supply the new instance to your test sequence:

.. code-block:: python

    ts = TestSequence(
        setup=setup,
        teardown=teardown,
        sequence=[T1(), T2()],
        archive_manager=mam
    )

On every test execution, your new custom ``save()`` method will be called and supplied with the data
for one execution of your test sequence.
