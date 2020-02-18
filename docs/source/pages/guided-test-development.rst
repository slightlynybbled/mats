Guided Test Development
==========================

Define Requirements
--------------------

First, we must define a set of requirements for our production test, which has nothing
to do with the code itself.  This will assist us in developing each test and, finally,
defining the test sequence.

The first test is a simple communication test.  Is the device communicating, True or
False?

The second test is a flow test in which the test communicates with an instrument
and reads the flow, applying a minimum and maximum flow.

Develop Hardware API
--------------------

Based on the test requirements, it is useful to create some hardware abstractions which
expose some of the functionality that we are interested in.  The hardware API development
effort is independent of the test, but will be necessary to most testing efforts and,
thus, we will cover a basic

The first abstraction communicates with the device and provides a property exposing
whether the device is communicating or not.  The development of this abstraction is
beyond the scope of this document; however, it is possible to assume a simple API
has been provided using a class called ``Device`` which has the property
``is_communicating``.

The second abstraction communicates with data acquisition hardware to determine the
flow of the system in liters / minute.  The simple api that we are assuming is
embodied in a class called ``Daq`` and exposed on a property ``flow``.

At this point, our directory structure has a couple of files in it which contain
the abstractions.  We will call these ``daq.py`` and ``device.py``:

.. code-block:: text

    root/
      daq.py
      device.py

Develop Individual Tests
------------------------

Communications Test
*******************

We will now create an ``automated_tests.py`` which will contain all of the automated
tests that we wish to execute, but not necessarily the order.

.. code-block:: text
   :emphasize-lines: 2

    root/
      automated_tests.py
      daq.py
      device.py

Within ``automated_tests.py``, we create our tests.

First, we import ``mats.Test`` and subclass our custom tests::

    from mats import Test

    class CommunicationTest(Test):
        def __init__(self):
            super().__init__(moniker='communications')

        def execute(self, is_passing):
            return None

    class FlowTest(Test):
        def __init__(self):
            super().__init__(moniker='flow')

        def execute(self, is_passing):
            return None

At this point, our tests don't do anything but implement the test class.  If this test
were executed within a sequence that saved data, it would end up applying no pass/fail
criteria and would save ``None`` to the headers fields ``communications`` and
``flow``.

First, we will focus on the communications test.  We will modify our imports to add
``from device import Device`` which gives us access to the device class.  In some
cases, the device will be instantiated already, in which case it might be more
appropriate to import the instance of the class rather than the class itself.  This
method is used in the :ref:`flow_test` outline.

.. code-block:: python
   :emphasize-lines: 2

   from mats import Test
   from device import Device

Next, we actually setup the device in preparation to use it by overriding the
``setup()`` method of ``Test``.

.. code-block:: python
   :emphasize-lines: 5, 6

    class CommunicationTest(Test):
        def __init__(self):
            super().__init__(moniker='communications')

        def setup(self, is_passing):
            self._device = Device()

        def execute(self, is_passing):
            return None

Now, it is time to acquire a bit of data.

.. code-block:: python
   :emphasize-lines: 9

    class CommunicationTest(Test):
        def __init__(self):
            super().__init__(moniker='communications')

        def setup(self, is_passing):
            self._device = Device()

        def execute(self, is_passing):
            return self._device.is_communicating

If the test sequence were executed at this point, there would be no pass/fail
criteria applied, but a ``True``/``False`` value would be saved under the
``communications`` header in the data file.

In order to apply criteria, we will use the ``pass_if`` parameter of
``Test.__init__()``

.. code-block:: python
   :emphasize-lines: 3

    class CommunicationTest(Test):
        def __init__(self):
            super().__init__(moniker='communications', pass_if=True)

        def setup(self, is_passing):
            self._device = Device()

        def execute(self, is_passing):
            return self._device.is_communicating

At this point, the test sequence will apply the pass fail condition to the results
of the ``execute()`` method.

The complete contents of ``automated_test.py``::

    from mats import Test
    from device import Device

    class CommunicationTest(Test):
        def __init__(self):
            super().__init__(moniker='communications', pass_if=True)

        def setup(self, is_passing):
            self._device = Device()

        def execute(self, is_passing):
            return self._device.is_communicating

    class FlowTest(Test):
        def __init__(self):
            super().__init__(moniker='flow')

        def execute(self, is_passing):
            return None


.. _flow_test:

Flow Test
*********

The development of the flow test will proceed similarly.  Just to change
the potential use case, we will assume that the ``daq.py`` creates the instance of
``daq`` that we can utilize directly.  This obviates the need to create the object
using the ``setup()`` method.  First we add the proper import statement and then
we utilize the ``daq.flow`` property to return the flow value on test execution.

.. code-block:: python
   :emphasize-lines: 3, 10

   from mats import Test
   from device import Device
   from daq import daq

   class FlowTest(Test):
      def __init__(self):
          super().__init__(moniker='flow')

      def execute(self, is_passing):
          return daq.flow

Next, we will apply minimum and maximum pass/fail criteria to the test:

.. code-block:: python
   :emphasize-lines: 3, 4

    class FlowTest(Test):
        def __init__(self):
            super().__init__(moniker='flow',
                             min_value=5.8, max_value=6.2)

        def execute(self, is_passing):
            return daq.flow

Using the ``min_value`` and ``max_value`` parameters allows us to apply quantitative
pass/fail criteria to the results of the execution step.

Complete Test Definition
************************

Finally, we have our complete test definition!

.. code-block:: python

    from mats import Test
    from device import Device
    from daq import daq

    class CommunicationTest(Test):
        def __init__(self):
            super().__init__(moniker='communications', pass_if=True)

        def setup(self, is_passing):
            self._device = Device()

        def execute(self, is_passing):
            return self._device.is_communicating

    class FlowTest(Test):
        def __init__(self):
            super().__init__(moniker='flow',
                             min_value=5.8, max_value=6.2)

        def execute(self, is_passing):
            return daq.flow

Create Test Sequence
--------------------

Up to this point, we have created some tests using the framework, but we haven't
actually done anything with them.  It would be wise to creat the ``TestSequence``
instance earlier than this point in most development processes; however, we have
chosen the order in order to better organize the presentation.

We will create the ``TestSequence`` within its own file, making our new file structure:

.. code-block:: text
   :emphasize-lines: 5

    root/
      automated_tests.py
      daq.py
      device.py
      test_sequence.py

Within ``test_sequence.py``, we will import our ``mats.TestSequence()`` along with
the ``CommunicationsTest()`` and ``FlowTest()`` that we previously defined:

.. code-block:: python

    from mats import TestSequence
    from automated_tests import FlowTest, CommunicationsTest

Now, we create our sequence as the instantiation of the test objects into a list:

.. code-block:: python

    sequence = [CommunicationsTest(), FlowTest()]

It is common to forget to instantiate the objects, so be sure that you include the
``()`` so that you are using instances of the test and not the test class.  The
order of the test sequence is defined by the order of the list, so a re-ordering
of this list is all that is required to refactor the order of the tests.

Now we create the ``TestSequence`` instance, being sure to capture an object handle
for the test sequence:

.. code-block:: python

    ts = TestSequence(sequence=sequence)

Finally, we run the test sequence one time:

.. code-block:: python

    ts.start()

The test will run to completion and output log data to the terminal.

The final full form of ``test_sequence.py``:

.. code-block:: python

    from mats import TestSequence
    from automated_tests import FlowTest, CommunicationsTest

    sequence = [CommunicationsTest(), FlowTest()]
    ts = TestSequence(sequence=sequence)

    ts.start()

Save the Data
-------------

At this point, we run the test and collect the data, but do not save it anywhere.
There are a couple of options for saving.  The first - and easiest - is to use the
built-in ``ArchiveManager``, which creates the most common formats of csv and csv-like
files common in manufacturing environments.  It also does some basic test change
detection in order to keep file headers separated as the test evolves over the life
of the project.

The most basic implementation of the ``ArchiveManager`` can be easily added to the
sequence:

.. code-block:: python
   :emphasize-lines: 2, 3, 6, 7

    from mats import TestSequence
    from automated_tests import FlowTest, \
                                CommunicationsTest, ArchiveManager

    sequence = [CommunicationsTest(), FlowTest()]
    am = ArchiveManager()
    ts = TestSequence(sequence=sequence, archive_manager=am)

    ts.start()

The only requirement for the object instance supplied to ``archive_manager`` is to
implement the ``save()`` method which will accept a ``dict`` containing the key: value
pairs on test completion.  In this way, it is very easy to supply custom archive
manager objects to extend the functionality of the archiving process.
