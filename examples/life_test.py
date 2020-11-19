"""
Implements an example life test which collects and saves data periodically.
Note that the test sequence does not have to be started by the user as it has
the `auto_start` and `auto_run` parameters set to `True`.
"""

from random import choice
from time import sleep

from mats import Test, TestSequence, ArchiveManager


class LifeTest(Test):
    def __init__(self):
        super().__init__(moniker='life test', pass_if=True)

    def setup(self, is_passing):
        # do_something_to_setup()
        sleep(0.1)

    def execute(self, is_passing):
        sleep(0.25)

        # simulate the collection of some data, then return it
        # so that the 'pass-if' condition may be applied
        result = choice([True] * 2 + [False])

        return result

    def teardown(self, is_passing):
        # do_something_to_teardown()
        sleep(0.1)


if __name__ == '__main__':
    ts = TestSequence(
        sequence=[LifeTest()],
        archive_manager=ArchiveManager(path='.'),
        auto_run=True,          # run the lifetest automatically after every iteration
        auto_start=True         # automatically start the sequence
    )

    sleep(5.0)
    ts.abort()
