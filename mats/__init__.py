"""
Manufacturing Automated Test System (MATS)

MATS takes care of all of the low-level tedium that every
manufacturing automated test must implement, such as:

 - test runner
 - test definition
 - auto saving of data
 - hardware setup / teardown
 - automatic GUI integration
"""

import coloredlogs
import logging

from mats.archiving import ArchiveManager

from mats.test import Test
from mats.test_sequence import TestSequence
from mats.tkwidgets import MatsFrame
from mats.version import __version__

__all__ = ['Test', 'TestSequence',
           'ArchiveManager', 'MatsFrame', '__version__']

coloredlogs.install(level='DEBUG')

logger = logging.getLogger(__name__)
