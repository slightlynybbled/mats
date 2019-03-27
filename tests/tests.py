"""
Automated test suite for the Automated Test Environment
"""
import pytest
import ate


@pytest.fixture
def blank_Test():
    yield ate.Test('test')

@pytest.fixture
def pass_if_Test():
    yield ate.Test('test', pass_if=True)


@pytest.fixture
def bracketed_Test():
    yield ate.Test('test', min_value=1.0, max_value=2.0)


def test_ate_version():
    assert ate.__version__


def test_Test_creation(blank_Test):
    t = blank_Test

    assert t.moniker == 'test'
    assert t.status == 'waiting'


def test_Test_class_creation_with_pass_if(pass_if_Test):
    t = pass_if_Test

    assert t.moniker == f'test (pass if=True)'
    assert t._pass_if is True
    assert t._min_value is None
    assert t._max_value is None


def test_Test_creation_with_min_and_max(bracketed_Test):
    t = bracketed_Test

    assert t.moniker == f'test (min=1.0, max=2.0)'
    assert t._pass_if is None
    assert t._min_value == 1.0
    assert t._max_value == 2.0

