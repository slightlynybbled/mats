Contribution Guidelines
=======================

Guidelines for new Issues
-------------------------

todo: Guidelines for issues...

Guidelines for Pull Requests
----------------------------

I am not a full-time project maintainer.  I'm a dude with a job.  That means
that pull requests have to be relatively self-contained in order to make the
cut.  Having said that, I don't think that the bar is too high in this
instance.

New pull requests shall:

* have an explanation of the feature or bugfix that they are implementing (preferabley with an issue number to refer to)
* have complete test coverage for that feature/bugfix
* be `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ compliant as defined by `flake8 <http://flake8.pycqa.org/en/latest/>`_ test

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

Creating a Branch
-----------------


