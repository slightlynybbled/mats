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
