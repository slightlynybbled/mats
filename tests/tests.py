"""
Automated test suite for the Automated Test Environment
"""
import pytest
import ate


def test_version():
    assert ate.__version__
