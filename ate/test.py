import logging



class Test:
    """
    A test is the most basic unit of an executing test sequence.  Within
    a test, we may have a setup(), execute(), and teardown() method.  Only the
    `execute()` method is required to be overridden.
    """

    def __init__(self, moniker, loglevel=logging.DEBUG):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self.moniker = moniker
        self.test_is_passing = None
        self.status = 'waiting'

    def _setup(self, aborted=False):
        """
        Pre-execution method used for logging and housekeeping.
        :return:
        """
        self._logger.info(f'setting up "{self.moniker}"')

        self.test_is_passing = True
        self.status = 'running' if not aborted else 'aborted'

        setup_value = self.setup(aborted)
        self.status = 'running' if not aborted else 'aborted'
        return setup_value

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

        teardown_value = self.teardown(aborted=aborted)
        self.status = 'complete'

        return teardown_value

    def reset(self):
        self.status = 'waiting'

    def setup(self, aborted=False):
        """
        Abstract method intended to be overridden by subclass

        :param aborted: True if the test was aborted or False if not
        :return: None if no data is to be saved, ('key', 'value') if data is to be saved
        """
        return None

    def execute(self, aborted=False):
        """
        Abstract method intended to be overridden by subclass

        :param aborted: True if the test was aborted or False if not
        :return: None if no data is to be saved, ('key', 'value') if data is to be saved
        """
        raise NotImplementedError

    def teardown(self, aborted=False):
        """
        Abstract method intended to be overridden by subclass

        :param aborted: True if the test was aborted or False if not
        :return: None if no data is to be saved, ('key', 'value') if data is to be saved
        """
        return None
