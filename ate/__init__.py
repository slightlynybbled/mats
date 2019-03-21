import coloredlogs

coloredlogs.install(level='DEBUG')

from ate.test import Test
from ate.test_sequence import TestSequence
from ate.version import __version__

__all__ = ['Test', 'TestSequence', '__version__']
