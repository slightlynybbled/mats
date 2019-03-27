"""
Automated test suite for the Automated Test Environment
"""
import pytest
import ate


@pytest.fixture
def blank_Test():
    class T(ate.Test):
        def __init__(self):
            super().__init__('test')

        def execute(self, aborted, is_passing):
            return None

    yield T()

@pytest.fixture
def pass_if_Test():
    class T(ate.Test):
        def __init__(self):
            super().__init__('test', pass_if=True)

        def execute(self, aborted, is_passing):
            return None

    yield T()


@pytest.fixture
def bracketed_Test():
    class T(ate.Test):
        def __init__(self):
            super().__init__('test', min_value=1.0, max_value=2.0)

        def execute(self, aborted, is_passing):
            return None

    yield T()


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


def test_Test_execute_not_implemented():
    t = ate.Test('test')
    with pytest.raises(NotImplementedError):
        t._execute(aborted=False, is_passing=True)

def test_Test_blank_setup_execute_teardown(blank_Test):
    t = blank_Test

    # check values before _setup()
    assert t.is_passing is None
    assert t.status == 'waiting'

    t._setup(aborted=False, is_passing=True)

    # check values after _setup()
    assert t.is_passing is True
    assert t.status == 'running'

    t._execute(aborted=False, is_passing=True)

    assert t.is_passing is True
    assert t.status == 'running'

    t._teardown(aborted=False, is_passing=True)

    assert t.is_passing is True
    assert t.status == 'complete'
