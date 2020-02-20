Dealing with Hardware
---------------------

As this test is dedicated to hardware testing, we have to deal with hardware!  There
are basically two ways to connect to hardware for your test environment:

 1. Re-allocate hardware on each test sequence
 2. Allocate hardware one time at initialization, pass it into your ``Test`` elements

In many cases, the same hardware will be utilized for multiple tests.  For instance,
a DAQ commonly includes digital inputs, outputs, etc, therefore a single test
sequence will likely contain multiple ``Test`` instances that utilize the same physical
hardware.  In these cases, hardware may be allocated to global variables.  Often it is
more practical to allocate the hardware one time and simply pass around the instances.

Allocation within ``Test``
==========================
The allocation of hardware within the test is simple, but it may have a time impact
that may or may not be acceptable in the application.  An example of this may be
found within the :ref:`examples_simple_production_test`.

One-Time Allocation
===================

Hardware is allocated one time at the beginning of the program and the references
to the hardware are passed into each test sequence.  This saves quite a bit of
time on fast-running tests.  Hardware allocation is generally completed at the
beginning of program execution, so startup time may be impacted, but the test
sequence time can be truncated significantly since hardware allocation often
takes more time than the test sequence.  An example may be found at
:ref:`examples_simple_production_test_revisited`.

In general, it is recommended to allocate hardware one-time at the beginning
of the test sequence, especially in sequences that will utilize the same
hardware for multiple test executions.  This creates the most flexible
test sequences along with requiring fewer exception handling blocks (hardware
not connected or powered?), making overall code structure simpler.
