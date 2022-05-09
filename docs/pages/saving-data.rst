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

Data Formats
------------

At this time, the ``mats.ArchiveManager`` supports two different output formats, both of which are
tab-delimited text files.

Data Format 0
*************

The default ``ArchiveManager`` output format is in the form of a tab-separated values file with the
pass-fail criteria placed at the top of the file.  To specify this data format unambigously during
initialization, then specify during object instantiation ``ArchiveManager(data_format=0)``.

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

Data Format 1
*************

This data format intents to represent pass/fail constraints in the form of columns, meaning that
each column name that has a constraint will have one or more additional columns which specify that
column name with an additional modifier which describes the contraint.  For instance, if the column
names ``speed`` and ``speed >`` exist , then the ``speed >`` column indicates that speed must be
greater than the contents of the column.

.. code-block::

    datetime	pass	failed	communications test	communications test =	pump flow test	pump flow test >=	pump flow test <=	pressure test
    2022-05-09 06:49:10.689560	True		True	True	 6.22	5.6	6.4	 10.4
    2022-05-09 06:49:14.194518	True		True	True	 5.94	5.6	6.4	 10.4
    2022-05-09 06:49:17.922168	True		True	True	 6.02	5.6	6.4	 10.1
    2022-05-09 06:49:21.659276	False	pump flow test	True	True	 6.46	5.6	6.4	 10
    2022-05-09 06:49:25.167991	False	pump flow test	True	True	 5.53	5.6	6.4	 10.1
    2022-05-09 06:49:28.675185	False	communications test	False	True	 6.02	5.6	6.4	 10.5
    2022-05-09 06:49:32.628712	False	communications test	False	True	 6.03	5.6	6.4	 11.2
    2022-05-09 06:49:58.689147	False	pump flow test	True	True	 6.57	5.6	6.4	 10.5
    2022-05-09 06:50:02.204322	False	communications test	False	True	 6.16	5.6	6.4	 10.2
    2022-05-09 06:50:05.725033	False	pump flow test	True	True	 6.44	5.6	6.4	 11.1
    2022-05-09 06:50:09.246196	True		True	True	 6.34	5.6	6.4	 10.1
    2022-05-09 06:50:12.865606	True		True	True	 5.72	5.6	6.4	 10.6
    2022-05-09 06:50:16.603413	False	pump flow test	True	True	 6.6	5.6	6.4	 10.2
    2022-05-09 06:50:20.227297	True		True	True	 6.14	5.6	6.4	 11.1
    2022-05-09 06:50:23.853710	True		True	True	 6.02	5.6	6.4	 10
    2022-05-09 06:50:27.366909	False	communications test;pump flow test	False	True	 6.42	5.6	6.4	 10.2
    2022-05-09 06:50:30.866149	True		True	True	 6.36	5.6	6.4	 10
    2022-05-09 06:50:34.383827	False	pump flow test	True	True	 6.65	5.6	6.4	 10.8

Note that `failed` column contains strings which, when multiple failures are present, are separated by semicolons.
This format allows easy plotting of values vs. constraints over time.

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
