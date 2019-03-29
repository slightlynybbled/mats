"""
Automated test suite for the Automated Test Environment.  This file focuses
on testing the ``TestSequence`` class.
"""
from time import sleep
import pytest
import ate


test_counter = 0  # use this to keep track of some test execution counts


class T_normal_1(ate.Test):
    def __init__(self):
        super().__init__('test 1')

    def execute(self, is_passing):
        sleep(0.2)
        return None

    def teardown(self, is_passing):
        global test_counter
        test_counter += 1


class T_normal_2(ate.Test):
    def __init__(self):
        super().__init__('test 2')

    def execute(self, is_passing):
        return None


class T_aborted(ate.Test):
    def __init__(self):
        super().__init__('test aborting')

    def execute(self, is_passing):
        self.abort()
        return None


class T_failing(ate.Test):
    def __init__(self):
        super().__init__('test failing', pass_if=True)

    def execute(self, is_passing):
        return False


class T_setup_exception(ate.Test):
    def __init__(self):
        super().__init__('test setup exception')

    def setup(self, is_passing):
        raise ValueError

    def execute(self, is_passing):
        return False


class T_execute_exception(ate.Test):
    def __init__(self):
        super().__init__('test execute exception')

    def execute(self, is_passing):
        raise ValueError


class T_teardown_exception(ate.Test):
    def __init__(self):
        super().__init__('test teardown exception')

    def execute(self, is_passing):
        return False

    def teardown(self, is_passing):
        raise ValueError

t1, t2 = T_normal_1(), T_normal_2()
ta, tf = T_aborted(), T_failing()


@pytest.fixture
def normal_test_sequence():
    global test_counter
    yield ate.TestSequence(sequence=[t1, t2])
    test_counter = 0


@pytest.fixture
def aborted_test_sequence():
    global test_counter
    yield ate.TestSequence(sequence=[ta])
    test_counter = 0


@pytest.fixture
def failed_test_sequence():
    global test_counter
    yield ate.TestSequence(sequence=[t1, tf])
    test_counter = 0


@pytest.fixture
def auto_test_sequence():
    global test_counter
    yield ate.TestSequence(sequence=[t1, t2], auto_start=True)
    test_counter = 0


@pytest.fixture
def auto_run_test_sequence():
    global test_counter
    yield ate.TestSequence(sequence=[t1, t2], auto_start=True, auto_run=True)
    test_counter = 0


def test_TestSequence_creation(normal_test_sequence):
    ts = normal_test_sequence

    assert ts.in_progress is False
    assert len(ts.test_names) == 2
    assert len(ts.tests) == 2


def test_TestSequence_retrieve_by_moniker(normal_test_sequence):
    ts = normal_test_sequence
    test = ts['test 1']
    assert test.moniker == 'test 1'


def test_TestSequence_retrieve_by_Test(normal_test_sequence):
    ts = normal_test_sequence
    test = ts[t1]
    assert test.moniker == 'test 1'


def test_TestSequence_retrieve_by_integer_should_error(normal_test_sequence):
    ts = normal_test_sequence
    with pytest.raises(TypeError):
        return ts[0]


def test_TestSequence_run(normal_test_sequence):
    ts = normal_test_sequence

    assert ts.ready
    ts.start()

    # wait a small amount of time, ensure that the test sequence has
    # begun and is in progress
    sleep(0.1)
    assert ts.in_progress is True

    while ts.in_progress is True:
        sleep(0.1)

    assert ts.in_progress is False


def test_TestSequence_run_attempted_interrupt(normal_test_sequence):
    ts = normal_test_sequence

    assert ts.ready
    ts.start()

    # wait a small amount of time, ensure that the test sequence has
    # begun and is in progress
    sleep(0.1)
    assert ts.in_progress is True
    ts.start()

    while ts.in_progress is True:
        sleep(0.1)

    assert ts.in_progress is False


def test_TestSequence_run_aborted(aborted_test_sequence):
    ts = aborted_test_sequence

    assert ts.ready
    ts.start()

    while ts.in_progress is True:
        sleep(0.1)

    aborted_test = ts['test aborting']
    assert aborted_test.aborted is True

    assert ts.is_aborted is True


def test_TestSequence_run_failed(failed_test_sequence):
    ts = failed_test_sequence

    assert ts.ready
    ts.start()

    while ts.in_progress is True:
        sleep(0.1)

    assert ts.is_passing is False
    assert ts.is_aborted is False


def test_TestSequence_auto_start(auto_test_sequence):
    ts = auto_test_sequence

    assert ts.in_progress is True

    while ts.in_progress is True:
        sleep(0.1)

    assert ts.ready


def test_TestSequence_auto_run(auto_run_test_sequence):
    global test_counter
    assert test_counter == 0

    ts = auto_run_test_sequence

    while ts.in_progress is True:
        sleep(1.0)

    ts.abort()

    assert test_counter > 2  # ensure that the test sequence
                             # has been executed multiple times


def test_TestSequence_setup_exception():
    counter = 0

    def on_test_exception():
        nonlocal counter
        counter += 1

    ts = ate.TestSequence(sequence=[T_setup_exception()],
                          teardown=on_test_exception)
    ts.start()

    while ts.in_progress is True:
        sleep(0.1)

    assert counter == 1


def test_TestSequence_execute_exception():
    counter = 0

    def on_test_exception():
        nonlocal counter
        counter += 1

    ts = ate.TestSequence(sequence=[T_execute_exception()],
                          teardown=on_test_exception)
    ts.start()

    while ts.in_progress is True:
        sleep(0.1)

    assert counter == 1


def test_TestSequence_teardown_exception():
    counter = 0

    def on_test_exception():
        nonlocal counter
        counter += 1

    ts = ate.TestSequence(sequence=[T_teardown_exception()],
                          teardown=on_test_exception)
    ts.start()

    while ts.in_progress is True:
        sleep(0.1)

    assert counter == 1
