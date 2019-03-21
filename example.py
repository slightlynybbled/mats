import logging
from time import sleep

from ate import Test
from ate import TestSequence


class CommunicationTest(Test):
    def __init__(self, loglevel=logging.INFO):
        super().__init__(moniker='communications test', loglevel=loglevel)

    def execute(self, aborted=False):
        if aborted:
            return None

        # should return a (key, value) which are the results of the test
        self.test_is_passing = False
        return 'dual comm', False


class PumpTest(Test):
    def __init__(self, loglevel=logging.INFO):
        super().__init__(moniker='pump test', loglevel=loglevel)

    def setup(self, aborted=False):
        return None

    def execute(self, aborted=False):
        if aborted:
            return None

        sleep(0.2)  # simulate long-running process

        # should return a (key, value) which are the results of the test
        self.test_is_passing = True
        return 'pump', False

    def teardown(self, aborted=False):
        return None


logging.basicConfig(level=logging.DEBUG)

# create the sequence of test objects
sequence = [CommunicationTest(), PumpTest()]
ts = TestSequence(sequence=sequence, auto_run=False, loglevel=logging.DEBUG)

print(ts.test_names)

print(ts['communications test'], ts[sequence[1]])

# start the test as many times as you wish!
for i in range(3):
    ts.start()
    sleep(0.3)
