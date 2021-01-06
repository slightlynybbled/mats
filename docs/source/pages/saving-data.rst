.. _saving-data-label:

Saving Data
===========

``MATS`` provides a very flexible module for saving data.

``ArchiveManager``
------------------

The builtin ``ArchiveManager`` is the default class built for saving data.  The ``ArchiveManager``
really implements one method, ``save()``.  The ``save()`` method accepts a ``dict`` as the parameter
which contains key: value pairs containing the results of a single test execution.

There is a very specific format for the dictionary which is passed into the ``save()`` method.  The
keys will represent the heading names.  The values of the ``dict`` will also be of a ``dict`` type
and will contain a "value" key with a value.  There is an optional nested "criteria" key which will
contain the "pass_if", "min" and "max" criteria, also as a dict.  An example would best illustrate:

.. code-block:: python

    {
      'datetime': {'value': '2021-01-05 22:07:26.181921'},
      'pass': {'value': True},
      'failed': {'value': '[]'},
      'communications test': {
        'value': True,
        'criteria': {'pass_if': True}
      },
      'pump flow test': {
        'value': 6.281,
        'criteria': {'min': 5.6, 'max': 6.4}
      }
    }

This dictionary will create the first row of data output below.  Any custom ``save()``
would need to support this data format.

Default Output Format
---------------------

The default ``ArchiveManager`` output format is in the form of a tab-separated values file with the
pass-fail criteria placed at the top of the file.

.. code-block::

    communications test:pass_if=True
    pump flow test:min=5.6,max=6.4

    datetime	pass	failed	communications test	pump flow test
    2021-01-05 22:07:26.181921	True	[]	True	 6.281
    2021-01-05 22:07:29.033729	True	[]	True	 6.028
    2021-01-05 22:07:32.447883	False	['communications test']	False	 6.200
    2021-01-05 22:07:35.525927	True	[]	True	 5.807
    2021-01-05 22:07:38.908803	True	[]	True	 6.377
    2021-01-05 22:07:42.471502	False	['communications test']	False	 6.100
    2021-01-05 22:07:46.206077	True	[]	True	 6.365
    2021-01-05 22:07:49.471290	False	['pump flow test']	True	 5.513
    2021-01-05 22:07:54.478150	False	['pump flow test']	True	 5.543
    2021-01-05 22:07:58.579855	False	['pump flow test']	True	 5.501
    2021-01-05 22:08:09.002198	True	[]	True	 5.747
    2021-01-05 22:08:12.868371	False	['communications test']	False	 5.926
    2021-01-05 22:08:16.376207	True	[]	True	 6.326
    2021-01-05 22:08:20.470113	True	[]	True	 6.063
    2021-01-05 22:08:57.587181	False	['pump flow test']	True	 6.612
    2021-01-05 22:09:01.960731	False	['pump flow test']	True	 5.569

Note that the spacing is a bit off because the tabs are not aligned well.  This file will
import into packages such as pandas quite well using::

    pd.read_csv('./path/to/file.txt', delimiter='\t', skiprows=3)

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
