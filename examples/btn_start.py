"""
Runs a GUI-based test which presents a start button to the user.  On press of
start button, the test will execute and indicate a pass or fail for each test
executed along with an overall pass/fail.
"""

from datetime import datetime, timedelta
import logging
import json
from random import random, choice
from time import sleep
import tkinter as tk

import coloredlogs

from mats import Test, TestSequence, ArchiveManager, __version__
from mats.tkwidgets import MatsFrame


def setup():
    print('some kind of sequence setup function to occur here, like turning on power supplies')


def teardown():
    print('some kind of sequence teardown function to occur here, '
          'like turning off power supplies or putting the fixture into a safe state')


def test_complete_callback(data, string):
    print(f'this is the data that gets passed to a callback:\n{json.dumps(data, indent=2)}')
    print(f'added some other string: {string}')


# The CommunicationTest class shows the minimum test structure that might
# be reasonably be implemented.  Only the `execute()` method is implemented.
class CommunicationTest(Test):
    def __init__(self, loglevel=logging.INFO):
        super().__init__(moniker='communications test',
                         pass_if=True,
                         loglevel=loglevel)

    # overriding the execute method
    def execute(self, is_passing):
        # a normal test would set `test_is_passing` based on real conditions, we
        # are implementing a random value here simply for illustrative purposes
        passing = choice([True] * 3 + [False])

        sleep(0.5)  # delay to simulate processing time

        # should return a (key, value) which are the results of the test
        return passing


# The PumpFlowTest implements the `setup' and `teardown` methods as well
# in order to demonstrate what that may look like
class PumpFlowTest(Test):
    def __init__(self, loglevel=logging.INFO):
        super().__init__(moniker='pump flow test',
                         min_value=5.6, max_value=6.4,
                         loglevel=loglevel)

    def setup(self, is_passing):
        # setting the speed of the pump might be something done in the setup,
        # including the wait time to speed up the pump, which we will
        # simulate with a 2s sleep
        sleep(2.0)

    def execute(self, is_passing):
        # simulate long-running process, such as
        # several flow measurement/averaging cycles
        sleep(0.1)
        flow = 5.5 + random() * 1.2

        # should return a (key, value) tuple which are the results of the test
        return flow

    def teardown(self, is_passing):
        # again, simulating another long-running process...
        sleep(0.1)


# A simple data-gathering exercise with no pass/fail criteria
class PressureTest(Test):
    def __init__(self, loglevel=logging.INFO):
        super().__init__(moniker='pressure test',
                         loglevel=loglevel)

    def execute(self, is_passing):
        # simulate long-running process, such as
        # several flow measurement/averaging cycles
        sleep(0.1)
        pressure = 10 + random() * 1.2

        # should return the results of the test
        return pressure


# A simple data-gathering exercise with no pass/fail criteria
class BurnInTest(Test):
    def __init__(self, loglevel=logging.INFO):
        super().__init__(moniker='burn in',
                         loglevel=loglevel)

    def execute(self, is_passing):
        # this is how you might check the abort status so that
        # a long-running process might be short-circuited
        if not is_passing and not self.aborted:
            return 0.0

        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=10)
        while datetime.now() < end_time and not self.aborted:
            sleep(0.1)

        # return the amount of burn-in time
        return (end_time - start_time).total_seconds()


if __name__ == '__main__':
    coloredlogs.install(level=logging.DEBUG)

    # create the sequence of test objects
    sequence = [CommunicationTest(), PumpFlowTest(),
                PressureTest(), BurnInTest()]
    ts = TestSequence(setup=lambda: setup(),
                      teardown=lambda: teardown(),
                      sequence=sequence,
                      archive_manager=ArchiveManager(data_format=1, preamble='some preamble text'),
                      callback=lambda data: test_complete_callback(data, 'my string!'),
                      loglevel=logging.DEBUG)

    window = tk.Tk()
    window.title(f'MATS {__version__}')

    tkate_frame = MatsFrame(window, ts, vertical=True)
    tkate_frame.grid(sticky='news')

    window.mainloop()
