from time import sleep
from random import choice, random

from mats import Test, TestSequence, ArchiveManager


# The CommunicationTest class shows the minimum test structure that might
# be reasonably be implemented.  Only the `execute()` method is implemented.
class CommunicationTest(Test):
    def __init__(self):
        super().__init__(moniker='communications test',
                         pass_if=True)

    # overriding the execute method
    def execute(self, is_passing):
        # a normal test would set `test_is_passing` based on real conditions,
        # we are implementing a random value here simply for illustrative
        # purposes
        is_communicating = choice([True] * 3 + [False])

        # should return a (key, value) which are the results of the test
        return is_communicating


# The FlowTest implements the `setup' and `teardown` methods as well in
# order to demonstrate what that may look like
class FlowTest(Test):
    def __init__(self):
        super().__init__(moniker='pump flow test',
                         min_value=5.6, max_value=6.4)

    def setup(self, is_passing):
        # setting the speed of the pump might be something done in the
        # setup, including the wait time to speed up the pump, which
        # we will simulate with a 2s sleep
        sleep(0.1)

    def execute(self, is_passing):
        # simulate long-running process, such as several flow
        # measurement/averaging cycles
        sleep(0.1)
        flow = 5.5 + random()

        # should return a (key, value) tuple which are the results of the test
        return flow

    def teardown(self, is_passing):
        # again, simulating another long-running process...
        sleep(0.1)


if __name__ == '__main__':
    # create the sequence of test objects
    sequence = [CommunicationTest(), FlowTest()]

    # create the archive manager
    am = ArchiveManager()

    # create the test sequence using the
    # sequence and archive manager objects from above
    ts = TestSequence(sequence=sequence,
                      archive_manager=am,
                      auto_run=False)

    # start the test as many times as you wish!
    for _ in range(3):
        ts.start()
        sleep(2.0)
