import coloredlogs
import logging

from ate.test import Test
from ate.test_sequence import TestSequence
from ate.archiving import ArchiveManager
from ate.version import __version__

__all__ = ['Test', 'TestSequence', 'ArchiveManager', '__version__']

coloredlogs.install(level='DEBUG')

logger = logging.getLogger(__name__)
logger.warning('The ATE package is being renamed to MATS (Manufacturing '
               'Automated Test System) in order to improve searchability.')
