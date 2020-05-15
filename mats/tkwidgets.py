import logging
from tkinter.ttk import Frame, Button, Label

from mats.test import Test
from mats.test_sequence import TestSequence

_light_green = '#66ff66'
_light_red = '#ff6666'
_light_yellow = '#ffff99'
_relief = 'sunken'
_label_padding = 5


class MatsFrame(Frame):
    """
    The frame that interacts with the test sequence in order to display the \
    test results as the test is executing.

    :param parent: the tk parent frame
    :param sequence: the instance of `TestSequence` to monitor
    :param vertical: if `True`, will stack tests vertically; \
    otherwise, horizontally
    :param start_btn: if `True`, will populate a start button; \
    otherwise, will not
    :param loglevel: the logging level, for instance 'logging.INFO'
    """
    def __init__(self, parent, sequence: TestSequence,
                 vertical=False, start_btn=True,
                 loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self._parent = parent
        super().__init__(self._parent)

        self._sequence = sequence

        arrow = '\u2b9e' if not vertical else '\u2b9f'

        row = 0
        col = 0

        if start_btn:
            Button(self, text='Start', command=sequence.start)\
                .grid(row=row, column=col, sticky='news')

        if not vertical:
            col += 1 if not vertical else 0
            row += 1 if vertical else 0
            Label(self, text=arrow, justify='center', anchor='center')\
                .grid(row=row, column=col, sticky='news')

        col += 1 if not vertical else 0
        row += 1 if vertical else 0

        self._test_status_frames = []
        for test in self._sequence.tests:
            self._test_status_frames.append(
                _TestLabel(self, test, vertical=vertical)
            )

        for i, tl in enumerate(self._test_status_frames):
            col += 1 if not vertical else 0
            row += 1 if vertical else 0

            tl.grid(row=row, column=col, sticky='news')

            if not vertical:
                col += 1 if not vertical else 0
                row += 1 if vertical else 0

                Label(self, text=arrow, justify='center', anchor='center')\
                    .grid(row=row, column=col, sticky='news')

        col += 1 if not vertical else 0
        row += 1 if vertical else 0

        self._complete_label = Label(self, text='-',
                                     anchor='center', justify='center')
        self._complete_label.grid(row=row, column=col, sticky='news')
        self._complete_label.config(relief=_relief, padding=_label_padding)

        self._update()

    def _update(self):
        if self._sequence.in_progress:
            self._complete_label.config(text='in progress',
                                        background=_light_yellow)
        elif self._sequence.is_aborted:
            self._complete_label.config(text='aborted',
                                        background=_light_red)
        elif self._sequence.is_passing:
            self._complete_label.config(text='pass',
                                        background=_light_green)
        else:
            self._complete_label.config(text='fail',
                                        background=_light_red)

        self.after(100, self._update)


class _TestLabel(Label):
    """
    A single instance of a test label frame.
    """
    def __init__(self, parent, test: Test, vertical: bool,
                 loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self._parent = parent
        super().__init__(self._parent)

        self._test = test

        if not vertical:
            self._label_text = self._test.moniker.replace(' ', '\n')
        else:
            self._label_text = self._test.moniker
        self.config(text=self._label_text, relief=_relief,
                    padding=_label_padding)

        self._label_bg_color = self.cget('background')

        self._update()

    def _update(self):
        """
        Updates the test label display based on the status of the Test

        :return: None
        """
        color = self._label_bg_color

        if self._test.status == 'waiting':
            color = self._label_bg_color
        elif self._test.status == 'running':
            color = _light_yellow
        elif self._test.status == 'aborted':
            color = _light_red
        elif not self._test.is_passing:
            color = _light_red
        elif self._test.is_passing:
            color = _light_green

        value = self._test.value
        if isinstance(value, float):
            value_str = f'{value: .03f}'
        else:
            try:
                value_str = f'{value.magnitude: .03f}'
            except AttributeError:
                value_str = f'{value}'

        if value_str and len(value_str) < 12:
            label_text = f'{self._label_text}\n({value_str})'
        else:
            label_text = self._label_text

        self.config(background=color, text=label_text)

        self.after(100, self._update)
