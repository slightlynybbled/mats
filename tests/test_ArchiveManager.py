"""
Automated test suite for the Automated Test Environment.  This file focuses
on testing the ``ArchiveManager`` class.
"""
from pathlib import Path
from os import remove

import pint
import pytest

import ate

unit = pint.UnitRegistry()


data_point_1 = {'t1': 10, 't2': 10.0, 't3': 'string 10'}
data_point_2 = {'t1': 10, 't2': 10.0, 't3': 'string 10', 't4': 1 * unit.rpm}


@pytest.fixture
def am():
    path = Path('.')

    yield ate.ArchiveManager(path=path)

    data_paths = [f for f in Path('.').iterdir() if 'data' in str(f)]
    for p in data_paths:
        remove(p)


def test_am_creation(am):
    assert am._delimiter == '\t'


def test_am_save(am):
    length = 5

    for _ in range(length):
        am.save(data_point_1)

    assert Path('data.csv').exists

    with open(Path('data.csv'), 'r') as f:
        assert len(f.readlines()) == (length + 1)


def test_am_save_new_header(am):
    length = 5

    for _ in range(length):
        am.save(data_point_1)

    for _ in range(length):
        am.save(data_point_2)

    data_paths = [f for f in Path('.').iterdir() if 'data' in str(f)]
    assert len(data_paths) == 2

    for p in data_paths:
        with open(p, 'r') as f:
            assert len(f.readlines()) == (length + 1)
