import logging
from time import sleep
from random import choice, random

from ate import Test, TestSequence, ArchiveManager


# The CommunicationTest class shows the minimum test structure that might be reasonably
# be implemented.  Only the `execute()` method is implemented.
class CommunicationTest(Test):
    def __init__(self):
        super().__init__(moniker='communications test',
                         pass_if=True)

    # overriding the execute method
    def execute(self, aborted, is_passing):
        # a normal test would set `test_is_passing` based on real conditions, we
        # are implementing a random value here simply for illustrative purposes
        is_communicating = choice([True] * 3 + [False])

        # should return a (key, value) which are the results of the test
        return is_communicating


# The FlowTest implements the `setup' and `teardown` methods as well in order to demonstrate what that may look like
class BurnIn(Test):
    def __init__(self):
        super().__init__(moniker='burnin', min_value=5.6, max_value=6.4)

    def setup(self, aborted, is_passing):
        # just wait for a while, maybe display a bit of a countdown...
        seconds = 0
        while seconds < 10:
            seconds += 1
            self._logger.info(f'burning in count: {seconds}s')
            sleep(1.0)

    def execute(self, aborted, is_passing):
        # check to see if the device is still communicating
        is_communicating = choice([True] * 3 + [False])

        # should return a (key, value) tuple which are the results of the test
        return is_communicating


if __name__ == '__main__':
    # create the sequence of test objects
    sequence = [CommunicationTest(), BurnIn()]

    # create the archive manager
    am = ArchiveManager()

    # create the test sequence using the sequence and archive manager objects from above
    ts = TestSequence(sequence=sequence,
                      archive_manager=am,
                      auto_run=False)

    # start the test as many times as you wish!
    ts.start()
