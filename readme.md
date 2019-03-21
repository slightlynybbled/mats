# Automated Test Environment (ATE)

`ATE` is a hardware-oriented test environment intended for production testing in a manufacturing 
environment.  The `ATE` framework is a test template and test sequence executor only, so there 
are no considerations for user interaction, meaning that you need to supply your own "start" button.

The ATE could be considered an automated test framework which imposes a consistent work flow and
reduces the amount of mind share that you need to dedicate to developing automated device tests.

# Usage

There are two primary classes within the ATE with which the coder will have to familiarize themselves, 
the `Test` class and the `TestSequence` class.

## `Test` Class

The user is expected to subclass the `Test` class and override the `execute()` method.  The user might
also override the `setup()` and/or `teardown()` methods.

Each instance of the `Test` class is an opportunity to gather data and apply pass/fail conditions to
that data.  Somewhere within the `execute()` method may reside a call of the `self.fail()` method based 
on conditions detected within the test.

The class should generally return a value, which will be appended to the sequence data `dict` under the key
that corresponds to the test `moniker`.  For instance, if the `moniker` was instantiated to be `flow test`,
and the test value is `6.2`, then the final data key will contain this association.

## `TestSequence` Class

Once one or more `Test` subclasses have been created, then the `TestSequence` class may be instantiated
and executed in order to apply an appropriate sequence and gather data into a single unified data
structure.

## Flow Diagram

There are two flow charts, each of which is loosely associated with the `Test` and `TestSequence`
classes outlined above.  The overall flow is represented by the flow diagram on the left which
coordinates the high-level flow of the test, such as start, abort, and callbacks, and automatic
start/run behaviors.

Each `Test` class has the option of implementing the `setup()`, `execute()`, and `teardown()` methods
which will be retrieved by the `TestSequence` appropriately.

![Flow Diagram](images/flow-diagram.jpg)

## Steps

 1. Import `Test` and `TestSequence` classes, structure project appropriately.
 2. Subclass the specific `Test` classes, one for each test in the intended sequence.
 3. (optional) Create any callbacks functions/methods that should be called after each test.
 4. (optional) Import and implement `ArchiveManager`
 5. Instantiate the `TestSequence`

## Example

### Example `Test` Classes

Here, we implement a minimum implementation of the `Test` class which may be utilized for a quick
test.  Note that only the `execute()` method is overridden, which is the minimum requirement.  This
class simulates a communications test which might be defined by the user that would output a `True`
if communication is valid or a 'False' if it is not.

    class CommunicationTest(Test):
        def __init__(self, loglevel=logging.INFO):
            super().__init__(moniker='communications test', loglevel=loglevel)
    
        # overriding the execute method
        def execute(self, aborted=False):
            # a normal test would set `test_is_passing` based on real conditions, we
            # are implementing a random value here simply for illustrative purposes
            passing = choice([True] * 3 + [False])
    
            if not passing:
                self.fail()
    
            # should return a value corresponding to the test results
            return passing

A more comprehensive hardware test may be found in the `PumpFlowTest`, which implements the optional
`setup()` and `teardown()` methods.

    class PumpFlowTest(Test):
        def __init__(self, loglevel=logging.INFO):
            super().__init__(moniker='pump flow test', loglevel=loglevel)
    
        def setup(self, aborted=False):
            # setting the speed of the pump might be something done in the setup, including
            # the wait time to speed up the pump, which we will simulate with a 2s sleep
            sleep(2.0)
    
        def execute(self, aborted=False):
            # user may abort the test based on the `aborted` or may
            # continue the test, at the author's discretion
            if aborted:
                return None
    
            # simulate long-running process, such as several flow measurement/averaging cycles
            sleep(0.1)
            flow = 5.5 + random()
    
            # apply conditions, fail the test if outside of those conditions
            if not 5.6 <= flow <= 6.4:
                self.fail()
    
            # should return a value corresponding to the test results
            return flow
    
        def teardown(self, aborted=False):
            # again, simulating another long-running process...
            sleep(0.1)

### Example `TestSequence` Class

Finally, the `TestSequence` must be implemented in which the tests are ordered and executed.

    # create the sequence of test objects
    sequence = [CommunicationTest(), PumpFlowTest()]
    ts = TestSequence(sequence=sequence, auto_run=False, loglevel=logging.DEBUG)

    # start the test as many times as you wish!
    for _ in range(6):
        ts.start()
        sleep(2.0)
        
In this case, we are simulating that the start sequence is begun every 2.0s.  Note that the
test actually takes longer to run than this 2.0s, therefore, the `start()` method will detect
this condition and will not allow an additional test to occur while the previous test is
still executing.
