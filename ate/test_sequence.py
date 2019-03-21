from datetime import datetime
import logging
from threading import Thread, active_count
from typing import List

from ate.test import Test

Sequence = List[Test]


class TestSequence:
    """
    The TestSequence will "knit" the sequence together by taking the objects and
    appropriately passing them through the process.

    :param sequence: a list of Tests
    :param auto_start: True if test is to be automatically started
    :param auto_run: True if the test is to be continually executed
    :param loglevel: the logging level
    """
    def __init__(self, sequence: Sequence, auto_start=False, auto_run=False, loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self._sequence = sequence
        self._auto_run = auto_run

        self.in_progress = False
        self._aborted = False
        self._test_data = {
            'datetime': str(datetime.now()),
            'pass': True,
            'failed': []
        }

        self.current_test = None

        if auto_start:
            self.start()

    def __getitem__(self, test_element: (str, Test)):
        test = None

        if isinstance(test_element, str):
            for t in self._sequence:
                if t.moniker == test_element:
                    test = t
                    break
        elif isinstance(test_element, Test):
            for t in self._sequence:
                if t == test_element:
                    test = t
                    break
        else:
            raise TypeError(f'"{test_element}" is of type "{type(test_element)}"; expected "str" or "Test"')

        if test is not None:
            return test

        raise KeyError(f'test "{test_element}" does not appear to be defined')

    @property
    def tests(self):
        return [test for test in self._sequence]

    @property
    def test_names(self):
        return [test.moniker for test in self._sequence]

    @property
    def ready(self):
        """
        Returns True if the test sequence is ready for another go at it, False if not
        :return: True or False
        """
        return not self.in_progress

    @property
    def is_passing(self):
        return self._test_data['pass']

    @property
    def is_aborted(self):
        return self._aborted

    def abort(self):
        """
        Abort the current test sequence
        :return: None
        """
        self._aborted = True

    def start(self):
        """
        Start a test sequence.  Will only work if a test sequence isn't already in progress
        :return: None
        """
        if self.in_progress:
            self._logger.warning('cannot begin another test when test is currently in progress')
            return

        thread = Thread(target=self.run_test)
        thread.start()

    def run_test(self):
        """
        Runs one instance of the test sequence.  Executes continually if
        :return:
        """
        self._logger.info('-' * 80)
        self.in_progress = True
        self._aborted = False
        self._test_data = {
            'datetime': str(datetime.now()),
            'pass': True,
            'failed': []
        }
        for test in self._sequence:
            test.reset()

        # begin the test sequence
        for test in self._sequence:
            self.current_test = test.moniker

            setup_result = test._setup(aborted=self._aborted)

            if setup_result is not None:
                k, v = setup_result
                self._test_data[k] = v

            test_result = test._execute(aborted=self._aborted)

            if test_result is not None:
                k, v = test_result
                self._test_data[k] = v

            teardown_result = test._teardown(aborted=self._aborted)

            if teardown_result is not None:
                k, v = teardown_result
                self._test_data[k] = v

            if not test.test_is_passing:
                self._test_data['pass'] = False
                self._test_data['failed'].append(test.moniker)

        self.in_progress = False

        self._logger.info('test sequence complete')
        self._logger.debug(f'test results: {self._test_data}')

        if self._auto_run and not self._aborted:
            thread = Thread(target=self.run_test)
            thread.start()
