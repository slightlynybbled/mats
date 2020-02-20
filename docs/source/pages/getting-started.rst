Getting Started
===============

Define Requirements
--------------------

First, we must define a set of requirements for our production test, which has nothing
to do with the code itself.  This will assist us in developing each test and, finally,
defining the test sequence.

The first test is a simple communication test.  Is the device communicating, True or
False?

The second test is a flow test in which the test communicates with an instrument
and reads the flow, applying a minimum and maximum flow.

In addition to the test requirements, it turns out that most hardware requires a power supply
or other physical component to be turned on or initialized.  We will deal with this in
our setup and teardown.

Develop Hardware API
--------------------

Based on the test requirements, it is useful to create some hardware abstractions which
expose some of the functionality that we are interested in.  The hardware API development
effort is independent of the test, but will be necessary to most testing efforts and,
thus, we will cover a basic implementation.

Our first object will be a power supply.  During the test, we will wish to control
a power supply on and off, perhaps even setting different voltages and current limits,
depending on the test.  For this example, we will only wish to turn on the power supply
at the beginning of the test and turn it off at the end of the test **or** if there
is some test fault.  We will call our power supply class ``PowerSupply`` and we will
store the ``PowerSupply`` class within ``power_supply.py``.

The next abstraction communicates with the device and provides a property exposing
whether the device is communicating or not.  The development of this abstraction is
beyond the scope of this document; however, it is possible to assume a simple API
has been provided using a class called ``Device`` which has the property
``is_communicating``.

The last abstraction communicates with data acquisition hardware to determine the
flow of the system in liters / minute.  The simple api that we are assuming is
embodied in a class called ``Daq`` and exposed on a property ``flow``.

At this point, our directory structure has a couple of files in it which contain
the abstractions.  We will call these ``daq.py`` and ``device.py``:

.. code-block:: text

    root/
      daq.py
      device.py
      power_supply.py


Create Automated Test File
--------------------------

We will now create an ``automated_tests.py`` which will contain all of the automated
tests that we wish to execute, setup function, and teardown function.

.. code-block:: text
   :emphasize-lines: 2

    root/
      automated_tests.py
      daq.py
      device.py
      power_supply.py

Within ``automated_tests.py``, we create our setup, teardown, and individual tests.

``setup()`` and ``teardown()``
------------------------------

For each test, we want to start in a known condition.  Use ``setup`` and ``teardown``
functions supplied to execute commands without saving any data.  The primary difference
between these functions and a ``Test`` is that the ``setup`` and ``teardown`` functions
do not save data.

In our case, the ``setup()`` function will turn on the power supply and the ``teardown()``
funciton will turn the power supply off.  If there is a critical error during the test,
the ``teardown()`` function will be executed, making it especially convenient for test
environments in which the safe must end in a guaranteed safe condition.

.. code-block:: python

   from time import sleep
   from power_supply import PowerSupply

   def setup_hardware(psu: PowerSupply):
       psu.set_voltage(12.0)
       psu.set_current(3.0)
       psu.on()
       sleep(1.0)  # allow power to stabilize

   def teardown_hardware(psu: PowerSupply):
      psu.off()
      sleep(0.1)

Note that our setup and teardown functions accept instances of hardware classes.  This
method makes it fairly easy to modularize and develop each function and ``Test`` class
efficiently.

Develop Individual Tests
------------------------

Communications Test
*******************

Within ``automated_tests.py``, import ``mats.Test`` and subclass our custom tests.

.. code-block:: python
   :emphasize-lines: 2, 15-20, 22-27

    from time import sleep
    from mats import Test
    from power_supply import PowerSupply

    def setup_hardware(psu: PowerSupply):
        psu.set_voltage(12.0)
        psu.set_current(3.0)
        psu.on()
        sleep(1.0)  # allow power to stabilize

    def teardown_hardware(psu: PowerSupply):
        psu.off()
        sleep(0.1)

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

.. note::

   The ``moniker`` of all test sequences must be unique or the test sequence will raise
   an error!

First, we will focus on the communications test.  We will modify our imports to add
``from device import Device`` which gives us access to the device class.  In some
cases, the device will be instantiated already, in which case it might be more
appropriate to import the instance of the class rather than the class itself.  In most
cases, it is worth it to externally allocate hardware and execute the test by passing
the class instance.

.. code-block:: python
   :emphasize-lines: 4

   from time import sleep
   from mats import Test
   from power_supply import PowerSupply
   from device import Device
   ...

Next, we will store an instance of the hardware within the ``CommunicationTest``
and so that we can utilize it during development.

.. code-block:: python
   :emphasize-lines: 2, 4

    class CommunicationTest(Test):
        def __init__(self, device: Device):
            super().__init__(moniker='communications')
            self._device = device

        def execute(self, is_passing):
            return None

Now, it is time to acquire a bit of data.

.. code-block:: python
   :emphasize-lines: 7

    class CommunicationTest(Test):
        def __init__(self, device: Device):
            super().__init__(moniker='communications')
            self._device = device

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
        def __init__(self, device: Device):
            super().__init__(moniker='communications', pass_if=True)
            self._device = device

        def execute(self, is_passing):
            return self._device.is_communicating

.. _flow_test:

Flow Test
*********

The development of the flow test will proceed similarly to the previous test.

.. code-block:: python
   :emphasize-lines: 4, 15

   from time import sleep
   from mats import Test
   from power_supply import PowerSupply
   from daq import daq
   from device import Device

   ...

   class FlowTest(Test):
      def __init__(self, daq: Daq):
          super().__init__(moniker='flow')
          self._daq = daq

      def execute(self, is_passing):
          return self._daq.flow

Next, we will apply minimum and maximum pass/fail criteria to the test:

.. code-block:: python
   :emphasize-lines: 3, 4

    class FlowTest(Test):
        def __init__(self, daq: Daq):
            super().__init__(moniker='flow',
                             min_value=5.8, max_value=6.2)
            self._daq = daq

        def execute(self, is_passing):
            return self._daq.flow

Using the ``min_value`` and ``max_value`` parameters allows us to apply quantitative
pass/fail criteria to the results of the execution step.

Complete Test Definition
************************

Finally, we have our complete test definition!

.. code-block:: python

    from time import sleep
    from mats import Test
    from power_supply import PowerSupply
    from daq import daq
    from device import Device

    def setup_hardware(psu: PowerSupply):
        psu.set_voltage(12.0)
        psu.set_current(3.0)
        psu.on()
        sleep(1.0)  # allow power to stabilize

    def teardown_hardware(psu: PowerSupply):
        psu.off()
        sleep(0.1)

    class CommunicationTest(Test):
        def __init__(self, device: Device):
            super().__init__(moniker='communications', pass_if=True)
            self._device = device

        def execute(self, is_passing):
            return self._device.is_communicating

    class FlowTest(Test):
        def __init__(self, daq: Daq):
            super().__init__(moniker='flow',
                             min_value=5.8, max_value=6.2)
            self._daq = daq

        def execute(self, is_passing):
            return self._daq.flow

Create Test Sequence
--------------------

Up to this point, we have created some tests using the framework, but we haven't
actually done anything with them.  It would be wise to creat the ``TestSequence``
instance earlier than this point in most development processes; however, we have
chosen the order in order to better organize the presentation.

We will create the ``TestSequence`` within its own file, making our new file structure:

.. code-block:: text
   :emphasize-lines: 6

    root/
      automated_tests.py
      daq.py
      device.py
      power_supply.py
      test_sequence.py

Allocate Hardware
*****************

Allocate some hardware within ``test_sequence.py``.

.. code-block:: python

    from power_supply import PowerSupply
    from daq import Daq
    from device import Device

    # allocate the hardware
    psu = PowerSupply()
    daq = Daq()
    device = Device()

Within ``test_sequence.py``, we will import our ``mats.TestSequence()`` along with
the ``CommunicationsTest()`` and ``FlowTest()`` that we previously defined:

.. code-block:: python
   :emphasize-lines: 1, 2, 3

    from mats import TestSequence
    from automated_tests import FlowTest, CommunicationsTest,\
        setup_hardware, teardown_hardware
    from power_supply import PowerSupply
    from daq import Daq
    from device import Device

    # allocate the hardware
    psu = PowerSupply()
    daq = Daq()
    device = Device()

Now, we create our sequence as the instantiation of the test objects into a list:

.. code-block:: python

    sequence = [
        CommunicationsTest(device),
        FlowTest(daq)
    ]

It is common to forget to instantiate the objects, so be sure that you include the
``()`` so that you are using instances of the test and not the test class.  The
order of the test sequence is defined by the order of the list, so a re-ordering
of this list is all that is required to refactor the order of the tests.

Now we create the ``TestSequence`` instance, supplying the sequence of tests, the ``setup``,
and the ``teardown`` functions, being sure to capture an object handle
for the test sequence:

.. code-block:: python

    ts = TestSequence(
            sequence=sequence,
            setup=lambda: setup_hardware(psu),
            teardown=lambda: teardown_hardware(psu)
        )

Finally, we run the test sequence one time:

.. code-block:: python

    ts.start()

The test will run to completion and output log data to the terminal.

The final full form of ``test_sequence.py``:

.. code-block:: python

    from mats import TestSequence
    from automated_tests import FlowTest, CommunicationsTest,\
        setup_hardware, teardown_hardware
    from power_supply import PowerSupply
    from daq import Daq
    from device import Device

    # allocate the hardware
    psu = PowerSupply()
    daq = Daq()
    device = Device()

    sequence = [
        CommunicationsTest(device),
        FlowTest(daq)
    ]

    ts = TestSequence(
        sequence=sequence,
        setup=lambda: setup_hardware(psu),
        teardown=lambda: teardown_hardware(psu)
    )

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
   :emphasize-lines: 1, 18, 24

    from mats import TestSequence, ArchiveManager
    from automated_tests import FlowTest, CommunicationsTest,\
        setup_hardware, teardown_hardware
    from power_supply import PowerSupply
    from daq import Daq
    from device import Device

    # allocate the hardware
    psu = PowerSupply()
    daq = Daq()
    device = Device()

    sequence = [
        CommunicationsTest(device),
        FlowTest(daq)
    ]

    am = ArchiveManager()

    ts = TestSequence(
        sequence=sequence,
        setup=lambda: setup_hardware(psu),
        teardown=lambda: teardown_hardware(psu)
        archive_manager=am
    )

    ts.start()

The only requirement for the object instance supplied to ``archive_manager`` is to
implement the ``save()`` method which will accept a ``dict`` containing the key: value
pairs on test completion.  In this way, it is very easy to supply custom archive
manager objects to extend the functionality of the archiving process.
