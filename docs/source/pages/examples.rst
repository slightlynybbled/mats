Examples
============

.. _examples_simple_production_test:

Simple Production Test
---------------------------

The standard production test consists of running the same test consistently on
every ``start()`` of the :ref:`classes_ate_testsequence`.  In this sequence,
the hardware is allocated on-the-fly within each test.

.. code-block:: python

    from time import sleep
    from random import choice, random

    from ate import Test, TestSequence, ArchiveManager

    from my_lib import Device, FlowSensor


    # A simple communications check with a device
    class CommunicationTest(Test):
        def __init__(self):
            super().__init__(moniker='communications test',
                             pass_if=True)

        def setup(self, is_passing):
            # initialize hardware communications
            self._device = Device()

            # wait for communication to begin...
            while not self._device.is_communicating:
                sleep(0.1)

        # overriding the execute method
        def execute(self, is_passing):
            # should return a the results of the test
            return self._device.is_communicating

        def teardown(self, is_passing):
            # de-allocate the hardware
            self._device.close()


    # The FlowTest implements the `setup' and `teardown` methods
    # as well in order to demonstrate what that may look like
    class FlowTest(Test):
        def __init__(self):
            super().__init__(moniker='pump flow test',
                             min_value=5.6, max_value=6.4)

        def setup(self, is_passing):
            # initialize hardware
            self._flow_sensor = FlowSensor()

            # wait for flow sensor to begin pulling values
            while self._flow_sensor.value is not None:
                sleep(0.1)

        def execute(self, is_passing):
            return self._flow_sensor.value

        def teardown(self, is_passing):
            # again, simulating another long-running process...
            self._flow_sensor.close()


    if __name__ == '__main__':
        # create the sequence of test objects
        sequence = [CommunicationTest(), FlowTest()]

        # create the archive manager
        am = ArchiveManager()

        # create the test sequence using the sequence and archive manager
        # objects from above
        ts = TestSequence(sequence=sequence,
                          archive_manager=am,
                          auto_run=False)

        # start the test as many times as you wish!
        for _ in range(3):
            ts.start()
            sleep(2.0)

.. _examples_simple_production_test_revisited:

Simple Production Test (revisited)
----------------------------------

The production test could also be done by allocating the hardware at the beginning
of the sequence and realizing some time-saving on each test execution of the test.

.. code-block:: python

    from time import sleep
    from random import choice, random

    from ate import Test, TestSequence, ArchiveManager

    from my_lib import Device, FlowSensor


    # A simple communications check with a device
    class CommunicationTest(Test):
        def __init__(self, device: Device):
            super().__init__(moniker='communications test',
                             pass_if=True)

            self._device = device

        # overriding the execute method
        def execute(self, is_passing):
            # should return a the results of the test
            return self._device.is_communicating


    class FlowTest(Test):
        def __init__(self, flow_sensor: FlowSensor):
            super().__init__(moniker='pump flow test',
                             min_value=5.6, max_value=6.4)

            self._flow_sensor = flow_sensor

        def execute(self, is_passing):
            return self._flow_sensor.value


    if __name__ == '__main__':
        # hardware allocated one time during program initialization, no
        # need to re-allocate during CommunicationTest and FlowTest
        device = Device()
        flow_sensor = FlowSensor()

        while not device.is_communicating and flow_sensor.value is not None:
            sleep(0.1)

        # create the sequence of test objects
        sequence = [
            CommunicationTest(device=device),
            FlowTest(flow_sensor=flow_sensor)
        ]

        # create the archive manager
        am = ArchiveManager()

        # create the test sequence using the sequence and archive manager
        # objects from above
        ts = TestSequence(sequence=sequence,
                          archive_manager=am,
                          auto_run=False)

        # start the test as many times as you wish!
        for _ in range(3):
            ts.start()
            sleep(2.0)


Production Test with Burn-In
-----------------------------

This test is similar to the above production test.  We use the setup method to provide a burn-in and provide a count.

.. code-block:: python

    from time import sleep
    from random import choice, random

    from ate import Test, TestSequence, ArchiveManager


    # The CommunicationTest class shows the minimum test structure
    # that might be reasonably be implemented.  Only the `execute()`
    # method is implemented.
    class CommunicationTest(Test):
        def __init__(self):
            super().__init__(moniker='communications test',
                             pass_if=True)

        # overriding the execute method
        def execute(self, is_passing):
            # a normal test would set `test_is_passing` based on
            # real conditions, we are implementing a random value
            # here simply for illustrative purposes
            is_communicating = choice([True] * 3 + [False])

            # should return a (key, value) which are the results of
            # the test
            return is_communicating


    # The FlowTest implements the `setup' and `teardown` methods as
    # well in order to demonstrate what that may look like
    class BurnIn(Test):
        def __init__(self):
            super().__init__(moniker='burnin', min_value=5.6, max_value=6.4)

        def setup(self, is_passing):
            # just wait for a while, maybe display a bit of a countdown...
            seconds = 0
            while seconds < 10:
                seconds += 1
                self._logger.info(f'burning in count: {seconds}s')
                sleep(1.0)

        def execute(self, is_passing):
            # check to see if the device is still communicating
            is_communicating = choice([True] * 3 + [False])

            # should return a (key, value) tuple which are the results
            # of the test
            return is_communicating


    if __name__ == '__main__':
        # create the sequence of test objects
        sequence = [CommunicationTest(), BurnIn()]

        # create the archive manager
        am = ArchiveManager()

        # create the test sequence using the sequence and archive
        # manager objects from above
        ts = TestSequence(sequence=sequence,
                          archive_manager=am,
                          auto_run=False)

        # start the test as many times as you wish!
        ts.start()

Life Test
-----------------

A test that simulates on-off cycles and keeps chugging... forever... and ever...

.. code-block:: python

    from random import choice
    from time import sleep

    from ate import Test, TestSequence, ArchiveManager


    class LifeTest(Test):
        def __init__(self):
            super().__init__(moniker='life test', pass_if=True)

        def setup(self, is_passing):
            # do_something_to_setup()
            sleep(0.1)

        def execute(self, is_passing):
            sleep(0.25)

            # simulate the collection of some data, then return it so
            # that the 'pass-if' condition may be applied
            result = choice([True] * 2 + [False])

            return result

        def teardown(self, is_passing):
            # do_something_to_teardown()
            sleep(0.1)


    if __name__ == '__main__':
        ts = TestSequence(
            sequence=[LifeTest()],
            archive_manager=ArchiveManager(path='.'),
            auto_run=True,   # run the test automatically after every iteration
            auto_start=True  # automatically start the sequence
        )