import coloredlogs

coloredlogs.install(level='DEBUG')

from ate.test import Test
from ate.test_sequence import TestSequence
from ate.archiving import ArchiveManager
from ate.version import __version__

__all__ = ['Test', 'TestSequence', 'ArchiveManager', '__version__']
