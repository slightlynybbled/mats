"""
Automated test suite for the Automated Test Environment.  This file focuses
on testing the ``Test`` class.
"""
import pytest
import mats


@pytest.fixture
def blank_Test():
    class T(mats.Test):
        def __init__(self):
            super().__init__('test')

        def execute(self, is_passing):
            return None

    yield T()


@pytest.fixture
def pass_if_Test():
    class T(mats.Test):
        def __init__(self):
            super().__init__('test', pass_if=True)

        def execute(self, is_passing):
            return None

    yield T()


@pytest.fixture
def min_Test():
    class T(mats.Test):
        def __init__(self):
            super().__init__('test', min_value=1.0)

        def execute(self, is_passing):
            return None

    yield T()


@pytest.fixture
def max_Test():
    class T(mats.Test):
        def __init__(self):
            super().__init__('test', max_value=2.0)

        def execute(self, is_passing):
            return None

    yield T()


@pytest.fixture
def bracketed_Test():
    class T(mats.Test):
        def __init__(self):
            super().__init__('test', min_value=1.0, max_value=2.0)

        def execute(self, is_passing):
            return None

    yield T()


@pytest.fixture
def aborted_in_setup_Test():
    class T(mats.Test):
        def __init__(self):
            super().__init__('test')

        def setup(self, is_passing):
            self.abort()

        def execute(self, is_passing):
            return None

    yield T()


@pytest.fixture
def aborted_in_execute_Test():
    class T(mats.Test):
        def __init__(self):
            super().__init__('test')

        def execute(self, is_passing):
            self.abort()
            return None

    yield T()


@pytest.fixture
def aborted_in_teardown_Test():
    class T(mats.Test):
        def __init__(self):
            super().__init__('test')

        def execute(self, is_passing):
            return None

        def teardown(self, is_passing):
            self.abort()

    yield T()


def test_ate_version():
    assert mats.__version__


def test_Test_execute_not_implemented():
    t = mats.Test('test')
    with pytest.raises(NotImplementedError):
        t._execute(is_passing=True)


def test_Test_creation(blank_Test):
    t = blank_Test

    assert t.moniker == 'test'
    assert t.status == 'waiting'


def test_Test_class_creation_with_pass_if(pass_if_Test):
    t = pass_if_Test

    assert t.moniker == 'test'
    assert t.criteria['pass_if'] is True


def test_Test_class_creation_min_only(min_Test):
    t = min_Test

    assert t.moniker == 'test'
    assert t.criteria['min'] == 1


def test_Test_class_creation_max_only(max_Test):
    t = max_Test

    assert t.moniker == 'test'
    assert t.criteria['max'] == 2


def test_Test_creation_with_min_and_max(bracketed_Test):
    t = bracketed_Test

    assert t.moniker == 'test'
    assert t.criteria['min'] == 1
    assert t.criteria['max'] == 2


def test_Test_blank_setup_execute_teardown(blank_Test):
    t = blank_Test

    # check values before _setup()
    assert t.is_passing is None
    assert t.status == 'waiting'

    t._setup(is_passing=True)

    # check values after _setup()
    assert t.is_passing is True
    assert t.status == 'running'

    t._execute(is_passing=True)

    # check values after _exeecute()
    assert t.is_passing is True
    assert t.status == 'running'

    t._teardown(is_passing=True)

    # check values after _teardown()
    assert t.is_passing is True
    assert t.status == 'complete'


def test_Test_pass_if_should_pass(pass_if_Test):
    t = pass_if_Test

    def execute(is_passing):
        return True

    # overwrite the `execute` method with the method above
    t.execute = execute

    t._setup(is_passing=True)
    t._execute(is_passing=True)

    assert t.is_passing is True


def test_Test_pass_if_should_fail(pass_if_Test):
    t = pass_if_Test

    def execute(is_passing):
        return False

    # overwrite the `execute` method with the method above
    t.execute = execute

    t._setup(is_passing=True)
    t._execute(is_passing=True)

    assert t.is_passing is False


def test_Test_min_should_pass(bracketed_Test):
    t = bracketed_Test

    def execute(is_passing):
        return 1.000001

    t.execute = execute

    t._setup(is_passing=True)
    t._execute(is_passing=True)

    assert t.is_passing is True


def test_Test_min_should_fail(bracketed_Test):
    t = bracketed_Test

    def execute(is_passing):
        return 0.9991

    t.execute = execute

    t._setup(is_passing=True)
    t._execute(is_passing=True)

    assert t.is_passing is False


def test_Test_max_should_pass(bracketed_Test):
    t = bracketed_Test

    def execute(is_passing):
        return 1.99999

    t.execute = execute

    t._setup(is_passing=True)
    t._execute(is_passing=True)

    assert t.is_passing is True


def test_Test_max_should_fail(bracketed_Test):
    t = bracketed_Test

    def execute(is_passing):
        return 2.001

    t.execute = execute

    t._setup(is_passing=True)
    t._execute(is_passing=True)

    assert t.is_passing is False


def test_Test_aborted_in_setup(aborted_in_setup_Test):
    t = aborted_in_setup_Test
    t._setup(is_passing=True)
    assert t.aborted is True

    t._execute(is_passing=False)
    assert t.aborted is True

    t._teardown(is_passing=False)
    assert t.aborted is True


def test_Test_aborted_in_execute(aborted_in_execute_Test):
    t = aborted_in_execute_Test

    t._setup(is_passing=True)
    assert t.aborted is False

    t._execute(is_passing=True)
    assert t.aborted is True

    t._teardown(is_passing=True)
    assert t.aborted is True


def test_Test_aborted_in_teardown(aborted_in_teardown_Test):
    t = aborted_in_teardown_Test
    t._setup(is_passing=True)
    assert t.aborted is False

    t._execute(is_passing=True)
    assert t.aborted is False

    t._teardown(is_passing=True)
    assert t.aborted is True


def test_Test_adding_extra_data(bracketed_Test):
    t = bracketed_Test

    def execute(is_passing):
        t.save_dict({'a': 1.0})
        return 1.99999

    t.execute = execute

    t._setup(is_passing=True)
    t._execute(is_passing=True)
    t._teardown(is_passing=True)

    assert t.is_passing is True
    assert t.saved_data['a'] == 1.0


def test_Test_significant_figures():
    class T(mats.Test):
        def __init__(self):
            super().__init__('test', significant_figures=4)

        def execute(self, is_passing):
            return 12345678

    test = T()
    test._execute(True)
    assert test.value == 12350000


def test_Test_significant_figures_string():
    """ if passed a string, then the significant figures should not alter it """
    class T(mats.Test):
        def __init__(self):
            super().__init__('test', significant_figures=4)

        def execute(self, is_passing):
            return '12345678'

    test = T()
    test._execute(True)
    assert test.value == '12345678'
