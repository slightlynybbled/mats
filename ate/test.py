import logging


class Test:
    """
    A test is the most basic unit of an executing test sequence.  Within
    a test, we may have a setup(), execute(), and teardown() method.  Only the
    `execute()` method is required to be overridden.

    :param moniker: a shortcut name for this particular test
    :param loglevel: the logging level to apply such as `logging.INFO`
    """

    def __init__(self, moniker, loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self.moniker = moniker
        self._test_is_passing = None
        self.status = 'waiting'

    @property
    def is_passing(self):
        return self._test_is_passing

    def _setup(self, aborted=False):
        """
        Pre-execution method used for logging and housekeeping.

        :return:
        """
        self._logger.info(f'setting up "{self.moniker}"')

        self._test_is_passing = True
        self.status = 'running' if not aborted else 'aborted'

        self.setup(aborted)
        self.status = 'running' if not aborted else 'aborted'

    def _execute(self, aborted=False):
        """
        Pre-execution method used for logging and housekeeping.

        :return:
        """
        self._logger.info(f'executing test "{self.moniker}"')

        executed_value = self.execute(aborted=aborted)
        self.status = 'running' if not aborted else 'aborted'

        return executed_value

    def _teardown(self, aborted=False):
        """
        Pre-execution method used for logging and housekeeping.

        :return:
        """
        self._logger.info(f'tearing down "{self.moniker}"')

        self.teardown(aborted=aborted)
        self.status = 'complete'

    def reset(self):
        """
        Reset the test status
        :return: None
        """
        self.status = 'waiting'

    def fail(self):
        """
        When called, will cause the test to fail.

        :return: None
        """
        self._test_is_passing = False

    def setup(self, aborted=False):
        """
        Abstract method intended to be overridden by subclass

        :param aborted: True if the test was aborted or False if not
        :return: None
        """
        pass

    def execute(self, aborted=False):
        """
        Abstract method intended to be overridden by subclass

        :param aborted: True if the test was aborted or False if not
        :return: value to be appended to the sequence dictionary
        """
        raise NotImplementedError

    def teardown(self, aborted=False):
        """
        Abstract method intended to be overridden by subclass

        :param aborted: True if the test was aborted or False if not
        :return: None
        """
        pass
