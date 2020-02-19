import coloredlogs
import logging

from mats.archiving import ArchiveManager
from mats import gui
from mats.test import Test
from mats.test_sequence import TestSequence

from mats.version import __version__

__all__ = ['Test', 'TestSequence', 'ArchiveManager', 'gui', '__version__']

coloredlogs.install(level='DEBUG')

logger = logging.getLogger(__name__)
