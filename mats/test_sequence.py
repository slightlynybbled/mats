import atexit
from datetime import datetime
import logging
from threading import Thread
import traceback
from typing import List

from mats.test import Test
from mats.archiving import ArchiveManager


Sequence = List[Test]


class TestSequence:
    """
    The TestSequence will "knit" the sequence together by taking the test \
    objects and appropriately passing them through the automated testing \
    process.

    :param sequence: a list of Tests
    :param archive_manager: an instance of ``ArchiveManager`` which will \
    contain the path and format-specific information
    :param auto_start: True if test is to be automatically started
    :param auto_run: True if the test is to be continually executed
    :param callback: function to call on each test sequence completion; \
    callback will be required to accept one parameter, which is the \
    dictionary of values collected over that test iteration
    :param setup: function to call before the test sequence
    :param teardown: function to call after the test sequence is complete, \
    even if there was a problem; common to have safety issues addressed here
    :param on_close: function to call when the functionality is complete; \
    for instance, when a GUI closes, test hardware may need to be de-allocated
    :param loglevel: the logging level
    """
    def __init__(self, sequence: Sequence,
                 archive_manager: ArchiveManager = None,
                 auto_start=False, auto_run=False, callback: callable = None,
                 setup: callable = None, teardown: callable = None,
                 on_close: callable = None,
                 loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        # protection just in case one or more of the instances contained
        # within the sequence were not instantiated properly, this will
        # instantiate them
        for i, test in enumerate(sequence):
            if not isinstance(test, Test):
                sequence[i] = test()

        if not self.__validate_sequence(sequence):
            raise ValueError('test monikers are not uniquely identified')

        self._sequence = sequence
        self._archive_manager = archive_manager
        self._auto_run = auto_run
        self._callback = callback
        self._setup = setup
        self._teardown = teardown
        self._on_close = on_close

        self.in_progress = False
        self._aborted = False
        self._test_data = {
            'datetime': {'value': str(datetime.now())},
            'pass': {'value': True},
            'failed': {'value': []}
        }

        self.current_test = None
        self._current_test_number = 0

        if self._teardown is not None:
            atexit.register(lambda: self._teardown_function())

        if auto_start:
            self._logger.info('"auto_start" flag is set, '
                              'beginning test sequence')
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
            raise TypeError(
                f'"{test_element}" is of type "{type(test_element)}"; '
                f'expected "str" or "Test"')

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
        Returns True if the test sequence is ready for another go at it, \
        False if not

        :return: True or False
        """
        return not self.in_progress

    @property
    def is_passing(self):
        """
        Returns True if the test sequence is currently passing, else False

        :return: True or False
        """
        return self._test_data['pass'].get('value')

    @property
    def is_aborted(self):
        """
        Returns True if the test sequence has been aborted, else False

        :return: True or False
        """

        return self._aborted

    @property
    def failed_tests(self):
        """
        Return a list of the tests which failed.

        :return: list of tests that failed
        """
        return self._test_data['failed'].get('value')

    @property
    def progress(self):
        """
        Returns a tuple containing (current_test_number, total_tests) in \
        order to give an indication of the progress of the test sequence.

        :return: tuple containing (current_test_number, total_tests)
        """
        return (self._current_test_number,
                len([test.moniker for test in self._sequence]))

    def close(self):
        """
        Allows higher level code to call the close functionality.
        """
        if self._on_close is not None:
            self._on_close()

    def __validate_sequence(self, sequence: List[Test]):
        moniker_set = set([t.moniker for t in sequence])

        if len(moniker_set) != len(sequence):
            return False

        return True

    def abort(self):
        """
        Abort the current test sequence.

        :return: None
        """
        self._aborted = True

    def start(self):
        """
        Start a test sequence.  Will only work if a test sequence isn't \
        already in progress.

        :return: None
        """
        if self.in_progress:
            self._logger.warning('cannot begin another test when test is '
                                 'currently in progress')
            return

        self.in_progress = True
        thread = Thread(target=self._run_test)
        thread.start()

    def _teardown_function(self):
        self._logger.info('tearing down test sequence by executing sequence teardown function')

        try:
            self._teardown()
        except Exception as e:
            self._logger.critical(f'critical error during '
                                  f'test teardown: {e}')
            self._logger.critical(str(traceback.format_exc()))

    def _run_test(self):
        """
        Runs one instance of the test sequence.  Executes continually if the \
        auto_run flag was set on initialization.

        :return: None
        """
        self._logger.info('-' * 80)
        self._aborted = False
        self._test_data = {
            'datetime': {'value': str(datetime.now())},
            'pass': {'value': True},
            'failed': {'value': []}
        }

        self._current_test_number = 0

        for test in self._sequence:
            test.reset()

        if self._setup is not None:
            self._setup()

        # begin the test sequence
        for i, test in enumerate(self._sequence):
            self._current_test_number = i

            if self._aborted:
                break

            self.current_test = test.moniker

            try:
                test._setup(is_passing=self.is_passing)
            except Exception as e:
                self._logger.critical(f'critical error during '
                                      f'setup of "{test}": {e}')
                self._logger.critical(str(traceback.format_exc()))
                self.abort()
                test.fail()

            if test.aborted:
                self.abort()
                break

            try:
                test_result = test._execute(is_passing=self.is_passing)
            except Exception as e:
                test_result = None
                self._logger.critical(f'critical error during '
                                      f'execution of "{test}": {e}')
                self._logger.critical(str(traceback.format_exc()))
                self.abort()
                test.fail()

            if test.aborted:
                self.abort()
                test.fail()
                break

            if test_result is not None:
                self._test_data[test.moniker] = {'value': test_result}

                criteria = test.criteria
                if criteria is not None:
                    self._test_data[test.moniker]['criteria'] = criteria

            try:
                test._teardown(is_passing=self.is_passing)
            except Exception as e:
                self._logger.critical(f'critical error during '
                                      f'teardown of "{test}": {e}')
                self._logger.critical(str(traceback.format_exc()))
                self.abort()
                test.fail()

            if test.aborted:
                self.abort()
                break

            if not test._test_is_passing:
                self._test_data['pass']['value'] = False
                self._test_data['failed']['value'].append(test.moniker)

            # if any data was specifically stored within a test,
            # then retrieve it and store it within the sequence
            # test data
            for k, v in test.saved_data.items():
                self._test_data[k]['value'] = v

        if not self._aborted and self._archive_manager is not None:
            self._archive_manager.save(self._test_data)

        self._logger.info('test sequence complete')
        self._logger.debug(f'test results: {self._test_data}')

        if self._teardown is not None:
            try:
                self._teardown()
            except Exception as e:
                self._logger.critical(f'an exception has occurred which may result '
                                      f'in an unsafe condition during sequence teardown: {e}')

        if self._callback is not None:
            self._logger.info(f'executing user-supplied callback function '
                              f'"{self._callback}"')
            try:
                self._callback(self._test_data)
            except Exception as e:
                self._logger.warning(f'an exception occurred during the callback sequence: {e}')

        self.in_progress = False

        if self._auto_run:
            if not self._aborted:
                self._logger.info('"auto_run" flag is set, looping')
                thread = Thread(target=self._run_test)
                thread.start()
            else:
                self._logger.warning('"auto_run" flag is set, but the test '
                                     'sequence was prematurely aborted')
