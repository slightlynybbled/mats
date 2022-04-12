"""
Automated test suite for the Automated Test Environment.

This file focuses on testing the ``ArchiveManager`` class.
"""
from pathlib import Path
from os import remove

import pint
import pytest

import mats

unit = pint.UnitRegistry()


data_point_1 = {'t1': {'value': 10},
                't2': {'value': 10.0},
                't3': {'value': 'string 10'},
                't5': {'value': True}}
data_point_2 = {'t1': {'value': 10},
                't2': {'value': 10.0},
                't3': {'value': 'string 10'},
                't4': {'value': 1 * unit.rpm},
                't5': {'value': True}}
data_point_3 = {'t1': {'value': 10},
                't2': {'value': 10.0, 'criteria': {'min': 9.0, 'max': 11.0}},
                't3': {'value': 'string 10'},
                't4': {'value': 1 * unit.rpm},
                't5': {'value': True, 'criteria': {'pass_if': True}}}


@pytest.fixture
def am0():
    path = Path('.')

    yield mats.ArchiveManager(path=path, data_format=0)

    data_paths = [f for f in Path('.').iterdir() if 'data' in str(f)]
    for p in data_paths:
        remove(p)


@pytest.fixture
def am1():
    path = Path('.')

    yield mats.ArchiveManager(path=path, data_format=1)

    data_paths = [f for f in Path('.').iterdir() if 'data' in str(f)]
    for p in data_paths:
        remove(p)


@pytest.fixture
def am2():
    path = Path('.')

    yield mats.ArchiveManager(path=path, data_format=2)

    data_paths = [f for f in Path('.').iterdir() if 'data' in str(f)]
    for p in data_paths:
        remove(p)


def test_am_creation(am1, am2):
    assert am1._delimiter == '\t'
    assert am2._delimiter == '\t'


def test_am0_save(am0):
    length = 5

    for _ in range(length):
        am0.save(data_point_1)

    assert Path('data.txt').exists

    with open(Path('data.txt'), 'r') as f:
        assert len(f.readlines()) == (length + 2)


def test_am1_save(am1):
    length = 5

    for _ in range(length):
        am1.save(data_point_1)

    assert Path('data.txt').exists

    with open(Path('data.txt'), 'r') as f:
        assert len(f.readlines()) == (length + 1)


def test_am2_save(am2):
    length = 5

    for _ in range(length):
        with pytest.raises(ValueError):
            am2.save(data_point_1)


def test_am0_save_with_criteria(am0):
    am0.save(data_point_3)

    data = data_point_3.copy()
    data['t5']['value'] = False
    am0.save(data_point_3)

    with Path('data.txt').open('r') as f:
        assert len(f.readlines()) == 6


def test_am1_save_with_criteria(am1):
    am1.save(data_point_3)

    data = data_point_3.copy()
    data['t5']['value'] = False
    am1.save(data_point_3)

    with Path('data.txt').open('r') as f:
        assert len(f.readlines()) == 3


def test_am0_save_new_header(am0):
    length = 5

    for _ in range(length):
        am0.save(data_point_1)

    for _ in range(length):
        am0.save(data_point_2)

    data_paths = [f for f in Path('.').iterdir() if 'data' in str(f)]
    assert len(data_paths) == 2

    for p in data_paths:
        with open(p, 'r') as f:
            assert len(f.readlines()) == (length + 2)


def test_am1_save_new_header(am1):
    length = 5

    for _ in range(length):
        am1.save(data_point_1)

    for _ in range(length):
        am1.save(data_point_2)

    data_paths = [f for f in Path('.').iterdir() if 'data' in str(f)]
    assert len(data_paths) == 2

    for p in data_paths:
        with open(p, 'r') as f:
            assert len(f.readlines()) == (length + 1)
