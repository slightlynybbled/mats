import coloredlogs
import logging

from mats.test import Test
from mats.test_sequence import TestSequence
from mats.archiving import ArchiveManager
from mats.version import __version__

__all__ = ['Test', 'TestSequence', 'ArchiveManager', '__version__']

coloredlogs.install(level='DEBUG')

logger = logging.getLogger(__name__)
logger.warning('The ATE package is being renamed to MATS (Manufacturing '
               'Automated Test System) in order to improve searchability.')
