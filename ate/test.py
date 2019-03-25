import logging


class Test:
    """
    A test is the most basic unit of an executing test sequence.  Within
    a test, we may have a setup(), execute(), and teardown() method.  Only the
    `execute()` method is required to be overridden.

    :param moniker: a shortcut name for this particular test
    :param loglevel: the logging level to apply such as `logging.INFO`
    """

    def __init__(self, moniker, max_value=None, min_value=None, pass_if=None, loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self.moniker = moniker
        self._max_value, self._min_value, self._pass_if = max_value, min_value, pass_if

        self._test_is_passing = None
        self.value = None
        self.status = 'waiting'

        self.saved_data = {}

    @property
    def is_passing(self):
        return self._test_is_passing

    def _setup(self, aborted, is_passing):
        """
        Pre-execution method used for logging and housekeeping.

        :param aborted: True if the test was aborted or False if not
        :param is_passing: True if the test sequence is passing up to this point, else False
        :return:
        """
        self._logger.info(f'setting up "{self.moniker}"')

        self._test_is_passing = True
        self.value = None
        self.status = 'running' if not aborted else 'aborted'

        self.setup(aborted=aborted, is_passing=is_passing)
        self.status = 'running' if not aborted else 'aborted'

    def _execute(self, aborted, is_passing):
        """
        Pre-execution method used for logging and housekeeping.

        :param aborted: True if the test was aborted or False if not
        :param is_passing: True if the test sequence is passing up to this point, else False
        :return:
        """
        self._logger.info(f'executing test "{self.moniker}"')

        self.value = self.execute(aborted=aborted, is_passing=is_passing)

        if self._pass_if is not None:
            if self.value != self._pass_if:
                self.fail()
        elif self._min_value is not None:
            if self.value < self._min_value:
                self.fail()
        elif self._max_value is not None:
            if self.value > self._max_value:
                self.fail()

        self.status = 'running' if not aborted else 'aborted'

        return self.value

    def _teardown(self, aborted, is_passing):
        """
        Pre-execution method used for logging and housekeeping.

        :param aborted: True if the test was aborted or False if not
        :param is_passing: True if the test sequence is passing up to this point, else False
        :return:
        """
        self._logger.info(f'tearing down "{self.moniker}"')

        self.teardown(aborted, is_passing)
        self.status = 'complete'

    def reset(self):
        """
        Reset the test status
        :return: None
        """
        self.status = 'waiting'

    def save_dict(self, data: dict):
        self.saved_data = data.copy()

    def fail(self):
        """
        When called, will cause the test to fail.

        :return: None
        """
        self._test_is_passing = False

    def setup(self, aborted, is_passing):
        """
        Abstract method intended to be overridden by subclass

        :param aborted: True if the test was aborted or False if not
        :param is_passing: True if the test sequence is passing up to this point, else False
        :return: None
        """
        pass

    def execute(self, aborted, is_passing):
        """
        Abstract method intended to be overridden by subclass

        :param aborted: True if the test was aborted or False if not
        :param is_passing: True if the test sequence is passing up to this point, else False
        :return: value to be appended to the sequence dictionary
        """
        raise NotImplementedError

    def teardown(self, aborted, is_passing):
        """
        Abstract method intended to be overridden by subclass

        :param aborted: True if the test was aborted or False if not
        :param is_passing: True if the test sequence is passing up to this point, else False
        :return: None
        """
        pass
