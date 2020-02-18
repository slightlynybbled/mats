GUI
===

Since MATS doesn't include its own start button, the test must be started on some trigger.
Often, it is adequate to simply run the production test at startup and it will work just fine.
If you prefer user interaction, you will likely wish to have some sort of GUI elements, including
the `start` button for the user.

My preference is to use a package called `TkMATS <https://github.com/slightlynybbled/tkmats>`_
which will automatically read the entire test sequence and display each test to the user in a
user friendly manner.  I have been using TkMATS in production for over a year and I'm quite
pleased with the ease of implementation and by the user feedback.

How do you get started?  My workflow generally looks something like this:

 #. Create a text-only test sequence and name it something obvious, such as `sequence.py`
 #. Develop the `sequence.py` as a console program until I'm happy with the resulting test,
    including archiving data.
 #. Create a Tkinter root window.
 #. Within the Tkinter root window, create an instance of `tkmats.TkMatsFrame`, supplying the
    test sequence as a list.

The below GUI element is simple, yet powerful.  Note that each test that is executed will
light up green or red in addition to displaying an overall pass/fail status for the sequence.

.. image:: ../_static/tkmats-animation.gif

All else is up to you!
