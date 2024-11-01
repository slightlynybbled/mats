Contribution Guidelines
=======================

Guidelines for new Issues
-------------------------

There are a several types of issues.  The most common are bug fixes, but some
will be oriented toward feature requests.

New bugfix issues should contain a full description of how to repeat the
problem identified.  If the problem cannot be repeated, then the issue
may be closed due to lack of information.

Feature request issues may warrant discussion in that thread.  It is expected
that some features may be implemented in the future, but this project is not intended
to be the `pytest` or the `django` of manufacturing test and, thus, I don't anticipate
a large feature set.

Guidelines for Pull Requests
----------------------------

I am not a full-time project maintainer.  I'm a dude with a job.  That means
that pull requests have to be relatively self-contained in order to make the
cut.  Having said that, I don't think that the bar is too high in this
instance.

It is advised to create a pull request against one or more issues which are
already documented.  The risk of simply adding features is that your cool
new whiz-bang feature is simply not a part of the maintainer's vision for the
project... meaning that you just did a bunch of work for nothing.  Neither
of us wants that.

New pull requests shall:

* have an explanation of the feature or bugfix that they are implementing (preferabley with an issue number to refer to)
* have some test coverage for that feature/bugfix
* be `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ compliant

Environment & Prerequisites
---------------------------

This project is maintained using the `uv toolset <https://docs.astral.sh/uv/>`_.  As
a result, most of the commands you will see below use the UV toolset to get things
done consistently and easily.

Most of this guide assumes that you have forked the repository in github and have
cloned to your local machine.

.. code-block:: text

    $> git clone https://github.com/<your_user_name>/mats

Executing Automated Testing
---------------------------

This project uses `pytest <https://docs.pytest.org/en/stable/>`_ for automated testing.::

    $> uv run pytest


Then run the style checker using::

    $> ruff check --fix

Documentation
-------------

To build the documentation, navigate to the documents directory and execute sphinx::

    $> cd docs
    $docs/> uv run sphinx-build -b html . _build

The documentation will be located in `docs/_build` as a web page.

Future Development
------------------

Features that I foresee:

 * More dynamic ``ArchiveManager``
    * sqlite
    * excel
 * Qt-based GUI

Have `other requests <https://github.com/slightlynybbled/mats/issues>`_?
