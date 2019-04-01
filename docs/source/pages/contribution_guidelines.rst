Contribution Guidelines
=======================

Executing Automated Testing
---------------------------

The packages required in order to execute the automated testing can be found
in the `test_requirements.txt` file at the base of the
`github repository <https://github.com/slightlynybbled/ate>`_.  As of this
writing, the test coverage is at 96% and any new functionality will be required
to be backed up by testing.

To get set up for testing, fork the repository to your user.  You may then
clone the github repository, install all requirements, install the repository
in ``develop`` mode:

.. code-block:: text

    $> git clone https://github.com/<your_user_name>/ate
    $> pip install -r test_requirements.txt
    $> pip install -r requirements.txt
    $> python setup.py develop

Run all tests using::

    $> py.test tests/

Then run the style checker using::

    $> flake8 ate

