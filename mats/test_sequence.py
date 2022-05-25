import atexit
from datetime import datetime
import logging
from threading import Thread
import traceback
from time import sleep
from typing import List

from mats.test import Test
from mats.archiving import ArchiveManager

# State Machine - Using strings b/c we can relatively easily look
# for valid substrings to give more information in a concise way.
# For instance, one may be looking for the substring 'ready', but
# another function may look for the substring 'abort'.
# valid states:
#  - ready
#  - starting
#  - setting up
#  - executing tests
#  - tearing down
#  - complete / ready
#  - aborting
#  - aborted / ready
#  - exiting


class TestSequence:

    """
    The sequence or stack of ``Test`` objects to execute.

    The TestSequence will "knit" the sequence together by taking the test \
    objects and appropriately passing them through the automated testing \
    process.

    :param sequence: a list of Tests
    :param archive_manager: an instance of ``ArchiveManager`` which will \
    contain the path and data_format-specific information
    :param auto_run: an integer that determines how many times a test \
    sequence will be executed before stopping
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

    def __init__(
        self,
        sequence: List[Test],
        archive_manager: (ArchiveManager, None) = None,
        auto_run: (int, None) = None,
        callback: callable = None,
        setup: callable = None,
        teardown: callable = None,
        on_close: callable = None,
        loglevel=logging.INFO,
    ):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        # protection just in case one or more of the instances contained
        # within the sequence were not instantiated properly, this will
        # instantiate them
        for i, test in enumerate(sequence):
            if not isinstance(test, Test):
                sequence[i] = test()

        if not TestSequence.__validate_sequence(sequence):
            raise ValueError("test monikers are not uniquely identified")

        self._sequence = sequence
        self._archive_manager = archive_manager
        self._callback = callback
        self._setup = setup
        self._teardown = teardown
        self._on_close = on_close
        self._auto_run = auto_run
        self._state = "ready" if not auto_run else "starting"

        self._test_data = {
            "datetime": {"value": str(datetime.now())},
            "pass": {"value": True},
            "failed": {"value": []},
        }

        self.current_test = None
        self._current_test_number = 0

        if self._teardown is not None:
            atexit.register(self._teardown_function)

        self._thread = Thread(target=self._run_sequence, daemon=True)
        self._thread.start()

    def __getitem__(self, test_element: (str, Test)):
        """
        Returns the ``Test`` instance within the \
        sequence named ``test_element``.

        :param test_element: a string that matches the moniker
        """
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
                f'expected "str" or "Test"'
            )

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
        return "ready" in self._state

    @property
    def is_passing(self):
        """
        Returns True if the test sequence is currently passing, else False

        :return: True or False
        """
        return self._test_data["pass"].get("value")

    @property
    def is_aborted(self):
        """
        Returns True if the test sequence has been aborted, else False

        :return: True or False
        """
        return "abort" in self._state

    @property
    def failed_tests(self):
        """
        Return a list of the tests which failed.

        :return: list of tests that failed
        """
        return self._test_data["failed"].get("value")

    @property
    def progress(self):
        """
        Returns a tuple containing (current_test_number, total_tests) in \
        order to give an indication of the progress of the test sequence.

        :return: tuple containing (current_test_number, total_tests)
        """
        return (
            self._current_test_number,
            len([test.moniker for test in self._sequence]),
        )

    @property
    def in_progress(self):
        """
        Returns True if the test sequence is currently in progress, else False.

        :return: True if the test sequence is currently in progress, else False
        """
        return "ready" not in self._state

    def close(self):
        """
        Allows higher level code to call the close functionality.
        """
        self._state = "exiting"
        if self._on_close is not None:
            self._on_close()

    @staticmethod
    def __validate_sequence(sequence: List[Test]):
        moniker_set = set([t.moniker for t in sequence])

        if len(moniker_set) != len(sequence):
            return False

        return True

    def abort(self):
        """
        Abort the current test sequence.

        :return: None
        """
        if "ready" not in self._state:
            self._state = "aborting"
            [test.abort() for test in self._sequence]

    def start(self):
        """
        Start a test sequence.  Will only work if a test sequence isn't \
        already in progress.

        :return: None
        """
        if self.in_progress:
            self._logger.warning(
                "cannot begin another test when test is " "currently in progress"
            )
            return

        self._state = "starting"

    def _teardown_function(self):
        self._logger.info(
            "tearing down test sequence by " "executing sequence teardown function"
        )

        try:
            self._teardown()
        except Exception as e:
            self._logger.critical(f"critical error during " f"test teardown: {e}")
            self._logger.critical(str(traceback.format_exc()))

    def _reset_sequence(self):
        """
        Initializes the test sequence data, initializes each \
        `Test` in preparation for the next single execution \
        of the sequence.
        """

    def _run_sequence(self):
        """
        Runs one instance of the test sequence.

        :return: None
        """
        while self._state != "exiting":
            # wait at the ready (unless in auto-run mode)
            while "ready" in self._state:
                if self._auto_run and "abort" not in self._state:
                    self._logger.info(
                        '"auto_run" flag is set, ' "beginning test sequence"
                    )
                    self.start()
                else:
                    sleep(0.1)

            if self._state == "exiting":
                self._sequence_teardown()
                return

            self._sequence_setup()
            self._sequence_executing_tests()
            self._sequence_teardown()

            if "abort" not in self._state:
                if self._archive_manager is not None:
                    self._archive_manager.save(self._test_data)

            if self._auto_run:
                self._auto_run -= 1

            if "abort" in self._state:
                self._state = "aborted / ready"
            else:
                self._state = "complete / ready"

    def _sequence_setup(self):
        if "abort" in self._state:
            return

        self._state = "setting up"
        self._logger.info("-" * 80)
        self._test_data = {
            "datetime": {"value": str(datetime.now())},
            "pass": {"value": True},
            "failed": {"value": []},
        }

        self._current_test_number = 0

        for test in self._sequence:
            test.reset()

        if self._setup is not None:
            self._setup()

    def _sequence_executing_tests(self):
        if "abort" in self._state:
            return

        # begin the test sequence
        for i, test in enumerate(self._sequence):
            self._current_test_number = i

            if "abort" in self._state:
                self._logger.warning(
                    f"abort detected on test " f"{i}, exiting test sequence"
                )
                break

            self.current_test = test.moniker

            try:
                test._setup(is_passing=self.is_passing)
            except Exception as e:
                self._logger.critical(
                    f"critical error during " f'setup of "{test}": {e}'
                )
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
                self._logger.critical(
                    f"critical error during " f'execution of "{test}": {e}'
                )
                self._logger.critical(str(traceback.format_exc()))
                self.abort()
                test.fail()

            if test.aborted:
                self.abort()
                test.fail()
                break

            if test_result is not None:
                self._test_data[test.moniker] = {"value": test_result}

                criteria = test.criteria
                if criteria is not None:
                    self._test_data[test.moniker]["criteria"] = criteria

            try:
                test._teardown(is_passing=self.is_passing)
            except Exception as e:
                self._logger.critical(
                    f"critical error during " f'teardown of "{test}": {e}'
                )
                self._logger.critical(str(traceback.format_exc()))
                self.abort()
                test.fail()

            if test.aborted:
                self.abort()
                break

            if not test._test_is_passing:
                self._test_data["pass"]["value"] = False
                self._test_data["failed"]["value"].append(test.moniker)

            # if any data was specifically stored within a test,
            # then retrieve it and store it within the sequence
            # test data
            for k, v in test.saved_data.items():
                self._test_data[k]["value"] = v

    def _sequence_teardown(self):
        """
        Finishes up a test sequence by saving data, executing teardown \
        sequence, along with user callbacks.
        :return:
        """
        if "abort" not in self._state:
            self._state = "tearing down"

        self._logger.info("test sequence complete")
        self._logger.debug(f"test results: {self._test_data}")

        if self._teardown is not None:
            try:
                self._teardown()
            except Exception as e:
                self._logger.critical(
                    f"an exception has occurred which "
                    f"may result in an unsafe condition "
                    f"during sequence teardown: {e}"
                )

        if self._callback is not None:
            self._logger.info(
                f"executing user-supplied callback function " f'"{self._callback}"'
            )
            try:
                self._callback(self._test_data)
            except Exception as e:
                self._logger.warning(
                    f"an exception occurred during the callback sequence: {e}"
                )
