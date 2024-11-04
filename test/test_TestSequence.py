"""
Automated test suite for the Automated Test Environment.  This file focuses
on testing the ``TestSequence`` class.
"""
from os import path, remove
from time import sleep

import pytest

import mats


test_counter = 0  # use this to keep track of some test execution counts


class T_normal_1(mats.Test):
    def __init__(self):
        super().__init__('test 1', pass_if=0, significant_figures=1)

    def execute(self, is_passing):
        sleep(0.2)
        return 0

    def teardown(self, is_passing):
        global test_counter
        test_counter += 1


class T_normal_2(mats.Test):
    def __init__(self):
        super().__init__('test 2',
                         min_value=-1.0,
                         max_value=1.0,
                         significant_figures=2)

    def execute(self, is_passing):
        # provide a dummy number that
        # will definitely pass the criteria
        return 0.0121


class T_aborted(mats.Test):
    def __init__(self):
        super().__init__('test aborting')

    def execute(self, is_passing):
        sleep(0.1)
        self.abort()
        return None


class T_failing(mats.Test):
    def __init__(self):
        super().__init__('test failing', pass_if=True)

    def execute(self, is_passing):
        return False


class T_setup_exception(mats.Test):
    def __init__(self):
        super().__init__('test setup exception')

    def setup(self, is_passing):
        raise ValueError

    def execute(self, is_passing):
        return False


class T_execute_exception(mats.Test):
    def __init__(self):
        super().__init__('test execute exception')

    def execute(self, is_passing):
        raise ValueError


class T_teardown_exception(mats.Test):
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
    yield mats.TestSequence(sequence=[t1, t2])
    test_counter = 0


@pytest.fixture
def aborted_test_sequence():
    global test_counter
    yield mats.TestSequence(sequence=[t1, ta, t2])
    test_counter = 0


@pytest.fixture
def failed_test_sequence():
    global test_counter
    yield mats.TestSequence(sequence=[t1, tf])
    test_counter = 0


@pytest.fixture
def auto_run_sequence():
    global test_counter
    yield mats.TestSequence(sequence=[t1, t2],
                            auto_run=True)
    test_counter = 0


def test_TestSequence_creation(normal_test_sequence):
    ts = normal_test_sequence

    assert ts.in_progress is False
    assert len(ts.test_names) == 2
    assert len(ts.tests) == 2


def test_TestSequence_duplicate_monikers():
    with pytest.raises(ValueError):
        mats.TestSequence(sequence=[t1, t1, t1])


def test_TestSequence_uninstantiated_Tests():
    mats.TestSequence(sequence=[
        T_normal_1, T_normal_2
    ])


def test_TestSequence_empty_raises_TE():
    ts = mats.TestSequence(sequence=[
        T_normal_1, T_normal_2
    ])
    with pytest.raises(KeyError):
        ts['test 3']


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


def test_TestSequence_run():
    """
    Checking a normal test sequence.
    """
    ts = mats.TestSequence(sequence=[t1, t2])

    assert ts.ready
    ts.start()

    # wait a small amount of time, ensure that the test sequence has
    # begun and is in progress
    sleep(0.1)
    assert ts.in_progress is True

    while ts.in_progress is True:
        sleep(0.1)

    assert ts.in_progress is False


def test_TestSequence_close():
    """
    Checking a normal test sequence.
    """
    close_events = 0

    def on_close():
        nonlocal close_events
        close_events += 1

    ts = mats.TestSequence(sequence=[t1, t2], on_close=on_close)

    assert ts.ready
    ts.start()

    sleep(0.1)
    while ts.in_progress is True:
        sleep(0.1)

    assert close_events == 0
    ts.close()
    assert  close_events == 1


# running GUI testing appears to make pytest unstable, leaving here
# until i can decide how to handle
# def test_MatsFrame_run_default(root):
#     """
#     Same as a normal test sequence, but uses
#     a MatsFrame with default parameters.
#     """
#     ts = mats.TestSequence(sequence=[t1, t2])
#     mf = MatsFrame(parent=root, sequence=ts)
#     mf.grid()
#     sleep(0.5)
#
#     assert ts.ready
#     ts.start()
#
#     # wait a small amount of time, ensure that the test sequence has
#     # begun and is in progress
#     sleep(0.1)
#     assert ts.in_progress is True
#
#     while ts.in_progress is True:
#         sleep(0.1)
#
#     assert ts.in_progress is False
#
#     # wait for some of the frame to update so that frames may be exercised
#     sleep(1.0)
#     root.destroy()

# running GUI testing appears to make pytest unstable, leaving here
# until i can decide how to handle
# def test_MatsFrame_run_horizontal(root):
#     """
#     Same as a normal test sequence, vertical orientation
#     """
#     ts = mats.TestSequence(sequence=[t1, t2])
#     mf = MatsFrame(parent=root, sequence=ts, vertical=False)
#     mf.grid()
#     sleep(0.5)
#
#     assert ts.ready
#     ts.start()
#
#     # wait a small amount of time, ensure that the test sequence has
#     # begun and is in progress
#     sleep(0.1)
#     assert ts.in_progress is True
#
#     while ts.in_progress is True:
#         sleep(0.1)
#
#     assert ts.in_progress is False
#
#     # wait for some of the frame to update so that frames may be exercised
#     sleep(1.0)
#     root.destroy()


def test_TestSequence_run_attempted_interrupt():
    """
    Testing to ensure that an interrupted test sequence is not actually \
    interrupted.  This test should clearly show in the coverage and in the \
    logging messages.

    :return:
    """
    ts = mats.TestSequence(sequence=[t1, t2])

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
    assert ts.progress == (1, 2, )


def test_TestSequence_run_with_callback():
    """
    Testing to ensure that the callback is executed during a normal test \
    sequence.

    :param normal_test_sequence:
    :return:
    """
    count = 0

    def increment_count(data):
        nonlocal count
        count += 1

    ts = mats.TestSequence(
        sequence=[t1, t2],
        callback=increment_count)
    ts.start()

    while(ts.in_progress):
        sleep(0.1)

    assert count == 1


def test_TestSequence_run_aborted(aborted_test_sequence):
    """
    Testing to ensure that the test is aborted, the test indicates that it is \
    aborted and that the test sequence indicates that it is aborted.

    :param aborted_test_sequence:
    :return:
    """
    ts = aborted_test_sequence

    assert ts.ready
    ts.start()

    while ts.in_progress is True:
        sleep(0.1)

    aborted_test = ts['test aborting']
    assert aborted_test.aborted is True

    assert ts.is_aborted is True

# #testing GUI elements appears to make automated testing unstable
# def test_MatsFrame_run_aborted(root):
#     """
#     Same as a normal test sequence, but uses
#     a MatsFrame with default parameters.
#     """
#     ts = mats.TestSequence(sequence=[t1, ta, t2])
#     mf = mats.MatsFrame(parent=root, sequence=ts)
#     mf.grid()
#     sleep(0.5)
#
#     assert ts.ready
#     ts.start()
#
#     # wait a small amount of time, ensure that the test sequence has
#     # begun and is in progress
#     sleep(0.1)
#     assert ts.in_progress is True
#
#     while ts.in_progress is True:
#         sleep(0.1)
#
#     aborted_test = ts['test aborting']
#     assert aborted_test.aborted is True
#
#     assert ts.is_aborted is True
#     sleep(1.0)
#     root.destroy()


def test_TestSequence_run_failed(failed_test_sequence):
    """
    Ensures that a test sequence that fails will cause the test sequence \
    to fail but not indicate aborted.

    :param failed_test_sequence:
    :return:
    """
    ts = failed_test_sequence

    assert ts.ready
    ts.start()

    while ts.in_progress is True:
        sleep(0.1)

    assert ts.is_passing is False
    assert ts.is_aborted is False
    assert len(ts.failed_tests) == 1


def test_TestSequence_setup_exception():
    """
    Tests the case in which there is some exception that occurs during \
    the setup phase of the test.  THe test should execute the teardown
    sequence.

    :return: None
    """
    counter = 0

    def on_test_exception():
        nonlocal counter
        counter += 1

    ts = mats.TestSequence(sequence=[T_setup_exception()],
                           teardown=on_test_exception)
    ts.start()

    while ts.in_progress is True:
        sleep(0.1)

    assert counter == 1


def test_TestSequence_execute_exception():
    """
    Tests the case in which there is some exception that occurs during \
    the execution phase of the test.  THe test should execute the teardown \
    sequence.

    :return: None
    """
    counter = 0

    def on_test_exception():
        nonlocal counter
        counter += 1

    ts = mats.TestSequence(sequence=[T_execute_exception()],
                           teardown=on_test_exception)
    ts.start()

    while ts.in_progress is True:
        sleep(0.1)

    assert counter == 1


def test_TestSequence_setup():
    """Ensures that the "setup" function is called when specified."""
    def setup_function():
        with open('test_data.txt', 'w') as f:
            f.write('data')

    ts = mats.TestSequence(sequence=[t1, t2],
                           setup=setup_function)
    ts.start()
    while ts.in_progress is True:
        sleep(0.1)

    assert path.exists('test_data.txt')
    remove('test_data.txt')
