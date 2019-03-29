"""
Automated test suite for the Automated Test Environment.  This file focuses
on testing the ``ArchiveManager`` class.
"""
from pathlib import Path
from os import remove

import pytest
import ate


data_point = {'t1': 10, 't2': 10.0, 't3': 'string 10'}


@pytest.fixture
def am():
    path = Path('.')

    yield ate.ArchiveManager(path=path)

    if path.exists():
        try:
            remove(path / 'data.csv')
        except OSError:
            pass


def test_am_creation(am):
    assert am._delimiter == '\t'


def test_am_save(am):
    length = 5

    for _ in range(length):
        am.save(data_point)

    assert Path('data.csv').exists

    with open(Path('data.csv'), 'r') as f:
        assert len(f.readlines()) == (length + 1)
