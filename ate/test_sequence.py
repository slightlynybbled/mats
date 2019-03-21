from datetime import datetime
import logging
from threading import Thread, active_count
from typing import List

from ate.test import Test
from ate.archiving import ArchiveManager


Sequence = List[Test]


class TestSequence:
    """
    The TestSequence will "knit" the sequence together by taking the test objects and appropriately passing them through the automated testing process.

    :param sequence: a list of Tests
    :param archive_manager: an instance of ``ArchiveManager`` which will contain the path and format-specific information
    :param auto_start: True if test is to be automatically started
    :param auto_run: True if the test is to be continually executed
    :param callback: function to call on each test sequence completion; callback will be required to accept one parameter, which is the dictionary of values collected over that test iteration
    :param loglevel: the logging level
    """
    def __init__(self, sequence: Sequence, archive_manager: ArchiveManager=None,
                 auto_start=False, auto_run=False, callback: callable=None, loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self._sequence = sequence
        self._archive_manager = archive_manager
        self._auto_run = auto_run
        self._callback = callback

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
        """
        Returns instances of all tests contained within the ``TestSequence``

        :return: all tests as a list
        """
        return [test for test in self._sequence]

    @property
    def test_names(self):
        """
        Returns the names of the tests contained within the ``TestSequence``

        :return: the names of the tests as a list
        """
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
        Abort the current test sequence.

        :return: None
        """
        self._aborted = True

    def start(self):
        """
        Start a test sequence.  Will only work if a test sequence isn't already in progress.
        :return: None
        """
        if self.in_progress:
            self._logger.warning('cannot begin another test when test is currently in progress')
            return

        thread = Thread(target=self.run_test)
        thread.start()

    def run_test(self):
        """
        Runs one instance of the test sequence.  Executes continually if the auto_run flag was set on initialization.

        :return: None
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

            test._setup(aborted=self._aborted)

            test_result = test._execute(aborted=self._aborted)
            if test_result is not None:
                self._test_data[test.moniker] = test_result

            test._teardown(aborted=self._aborted)

            if not test._test_is_passing:
                self._test_data['pass'] = False
                self._test_data['failed'].append(test.moniker)

            # if any data was specifically stored within a test,
            # then retrieve it and store it within the sequence
            # test data
            for k, v in test.saved_data.items():
                self._test_data[k] = v

        if not self._aborted and self._archive_manager is not None:
            self._archive_manager.save(self._test_data)

        self.in_progress = False

        self._logger.info('test sequence complete')
        self._logger.debug(f'test results: {self._test_data}')

        if self._callback is not None:
            self._logger.info(f'executing user-supplied callback function "{self._callback}"')
            self._callback(self._test_data)

        if self._auto_run and not self._aborted:
            self._logger.info('"auto_run" flag is set, looping')
            thread = Thread(target=self.run_test)
            thread.start()
