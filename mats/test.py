import logging
from numbers import Number
from typing import Optional, Union

from sigfig import round


class Test:

    """
    The most basic unit of an executing test sequence.

    Within a test, we may have a setup(), execute(), and \
    teardown() method.  Only the `execute()` method is required \
    to be overridden.

    :param moniker: a shortcut name for this particular test
    :param min_value: the minimum value that is to be considered a pass, \
    if defined
    :param max_value: the maximum value that is to be considered a pass, \
    if defined
    :param pass_if: the value that must be present in order to pass, if defined
    :param significant_figures: the number of significant figures appropriate to the measurement
    :param loglevel: the logging level to apply such as `logging.INFO`
    """

    def __init__(
        self,
        moniker: str,
        min_value: Optional[Number] = None,
        max_value: Optional[Number] = None,
        pass_if: Optional[Union[str, bool, int]] = None,
        significant_figures: int = 4,
        loglevel=logging.INFO,
    ):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        criteria = {}
        if pass_if is not None:
            criteria["pass_if"] = pass_if
        if min_value is not None:
            criteria["min"] = min_value
        if max_value is not None:
            criteria["max"] = max_value

        self.moniker = moniker
        self._criteria = criteria if criteria else None
        self._significant_figures = significant_figures

        self._test_is_passing = None
        self.value = None
        self.aborted = False
        self.status = "waiting"

        self.saved_data = {}

    @property
    def is_passing(self):
        """
        Returns `True` if test is currently passing, else `False`

        :return: `True` if passing, else `False`
        """
        return self._test_is_passing

    @property
    def criteria(self):
        """
        Returns the test criteria as a `dict`

        :return: test criteria as a `dict`
        """
        return self._criteria

    def abort(self):
        """
        Causes current test status to abort

        :return: None
        """
        self.aborted = True

    def _setup(self, is_passing: bool):
        """
        Pre-execution method used for logging and housekeeping.

        :param is_passing: True if the test sequence is passing up to this \
        point, else False
        :return:
        """
        self._logger.info(f'setting up "{self.moniker}"')

        self._test_is_passing = True
        self.value = None
        self.status = "running" if not self.aborted else "aborted"

        self.aborted = False
        self.setup(is_passing=is_passing)
        self.status = "running" if not self.aborted else "aborted"

    def _execute(self, is_passing: bool):
        """
        Pre-execution method used for logging and housekeeping.

        :param is_passing: True if the test sequence is passing up to this \
        point, else False
        :return:
        """
        self.status = "running" if not self.aborted else "aborted"
        if self.aborted:
            self._logger.warning("aborted, not executing")
            return

        self._logger.info(f'executing test "{self.moniker}"')

        # execute the test and perform appropriate rounding
        value = self.execute(is_passing=is_passing)
        if isinstance(value, Number):
            try:
                value = round(value, self._significant_figures)
            except ValueError:
                self._logger.debug(f'could not apply significant digits to "{value}"')
        self.value = value

        if self._criteria is not None:
            if self._criteria.get("pass_if") is not None:
                if self.value != self._criteria["pass_if"]:
                    self._logger.warning(
                        f'"{self.value}" != pass_if requirement '
                        f'"{self._criteria["pass_if"]}", failing'
                    )
                    self.fail()
                else:
                    self._logger.info(
                        f'"{self.value}" == pass_if requirement '
                        f'"{self._criteria["pass_if"]}"'
                    )

            if self._criteria.get("min") is not None:
                if self.value < self._criteria["min"]:
                    self._logger.warning(
                        f'"{self.value}" is below the minimum '
                        f'"{self._criteria["min"]}", failing'
                    )
                    self.fail()
                else:
                    self._logger.info(
                        f'"{self.value}" is above the minimum '
                        f'"{self._criteria["min"]}"'
                    )

            if self._criteria.get("max") is not None:
                if self.value > self._criteria["max"]:
                    self._logger.warning(
                        f'"{self.value}" is above the maximum '
                        f'"{self._criteria["max"]}"'
                    )
                    self.fail()
                else:
                    self._logger.info(
                        f'"{self.value}" is below the maximum '
                        f'"{self._criteria["max"]}"'
                    )

        self.status = "running" if not self.aborted else "aborted"

        return self.value

    def _teardown(self, is_passing: bool):
        """
        Pre-execution method used for logging and housekeeping.

        :param is_passing: True if the test sequence is passing up to \
        this point, else False
        :return:
        """
        if self.aborted:
            self.status = "aborted"
            self._logger.warning("aborted, not executing")
            return

        self._logger.info(f'tearing down "{self.moniker}"')

        self.teardown(is_passing)
        self.status = "complete"

    def reset(self):
        """
        Reset the test status
        :return: None
        """
        self.status = "waiting"

    def save_dict(self, data: dict):
        """
        Allows a test to save additional data other than that returned \
        by ``execute()``

        :param data: key: value pairs of the data to be stored
        :return: None
        """
        self.saved_data = data.copy()

    def fail(self):
        """
        When called, will cause the test to fail.

        :return: None
        """
        self._test_is_passing = False

    def setup(self, is_passing: bool):
        """
        Abstract method intended to be overridden by subclass

        :param is_passing: True if the test sequence is passing up to this \
        point, else False
        :return: None
        """
        pass

    def execute(self, is_passing: bool):
        """
        Abstract method intended to be overridden by subclass

        :param is_passing: True if the test sequence is passing up to this \
        point, else False
        :return: value to be appended to the sequence dictionary
        """
        raise NotImplementedError

    def teardown(self, is_passing: bool):
        """
        Abstract method intended to be overridden by subclass

        :param is_passing: True if the test sequence is passing up to this \
        point, else False
        :return: None
        """
        pass
