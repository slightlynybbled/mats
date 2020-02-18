Introduction
--------------

The Manufacturing Automated Test System (MATS) is a framework for automating production testing suitable for manufacturing and
industrial environments.  The MATS will assist the user in defining the tests clearly and concisely and will execute the
written tests in the same sequence over and over, saving the production data from each run as the test sequence
is executed.

Installation
--------------

For most, simply ``pip install mats`` should do the trick.  You may wish to stroll over to the
`github repository <https://github.com/slightlynybbled/mats>`_, clone it, and ``python setup.py install`` if you prefer.

Key Concepts
------------

There are two primary classes to pay attention to within the MATS:
:ref:`classes_mats_test` and :ref:`classes_mats_testsequence`.  The ``TestSequence``
consists of a series of ``Tests``.  One complete run through the entire sequence
is initiated on utilization of the ``start()`` method.

.. image:: _static/flow-diagram.jpg

After each test sequence is completed, then there is an opportunity to save data using the
:ref:`classes_mats_archivemanager` or other object that implements the same ``save()`` method.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   pages/getting-started
   pages/dealing-with-hardware
   pages/examples
   pages/classes
   pages/gui.rst
   pages/contribution_guidelines.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
