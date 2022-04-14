import logging
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
        sleep(0.5)

        # simulate the collection of some data, then return it so
        # that the 'pass-if' condition may be applied
        result = choice([True] * 2 + [False])

        return result

    def teardown(self, is_passing):
        # do_something_to_teardown()
        sleep(0.1)


if __name__ == '__main__':
    from datetime import datetime, timedelta

    logger = logging.getLogger(__name__)

    ts = TestSequence(
        sequence=[LifeTest()],
        archive_manager=ArchiveManager(path='.'),
        auto_run=True,   # run the test automatically after every iteration
    )

    # allow the test to run for a complete minute, then abort
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(minutes=1)
    while datetime.now() < end_dt:
        sleep(0.1)

    logger.warning('TIME IS UP!')
    ts.abort()
    while ts.in_progress:
        sleep(0.1)

    logger.info(f'test time: {datetime.now() - start_dt}')
