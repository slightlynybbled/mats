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
        otherwise, horizontally; default is vertical, `True`
    :param start_btn: if `True`, will populate a start button; \
        otherwise, will not; default is `True`
    :param wrap: the number above which will start the next row or column
    :param loglevel: the logging level, for instance 'logging.INFO'
    """
    def __init__(self, parent, sequence: TestSequence,
                 vertical=True, start_btn=True, wrap: int = 6,
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
                .grid(row=0, column=0, sticky='news')

        status_frame = Frame(self)
        if vertical:
            status_frame.grid(row=1, column=0)
        else:
            Label(self, text=arrow, justify='center', anchor='center')\
                .grid(row=0, column=1, sticky='news')
            status_frame.grid(row=0, column=2)

        col += 1 if not vertical else 0
        row += 1 if vertical else 0

        self._test_status_frames = []
        for test in self._sequence.tests:
            self._test_status_frames.append(
                _TestLabel(status_frame, test, vertical=vertical)
            )

        row, col = 0, 0
        max_row = row
        max_col = col
        for tl in self._test_status_frames:
            if vertical:
                tl.grid(row=row, column=col, sticky='news')

                row += 1
                row %= wrap
                if row == 0:
                    col += 1
            else:
                tl.grid(row=row, column=col, sticky='news')

                col += 1
                col %= wrap
                if col == 0:
                    row += 1

            max_row = max(row, max_row)
            max_col = max(col, max_col)

        col += 1 if not vertical else 0
        row += 1 if vertical else 0

        self._complete_label = Label(self, text='-',
                                     anchor='center', justify='center')
        if vertical:
            self._complete_label.grid(row=2, column=0, sticky='news')
        else:
            self._complete_label.grid(row=0, column=3, sticky='news')
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

        criteria = self._test.criteria
        criteria_list = []
        criteria_string = ''
        if criteria is not None:
            for condition, value in criteria.items():
                if isinstance(value, bool) or isinstance(value, int) or isinstance(value, str):
                    cs = f'{condition}={value}'
                else:
                    cs = f'{condition}={value:.3g}'
                criteria_list.append(cs)
            criteria_string = ','.join(criteria_list)

        self._label_text = f'{self._test.moniker}'
        if criteria_string:
            self._label_text += f'\n{criteria_string}'

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
            value_str = f'{value:.3g}'
        else:
            try:
                value_str = f'{value.magnitude: .03g}'
            except AttributeError:
                value_str = f'{value}'

        if value_str and len(value_str) < 12:
            label_text = f'{self._label_text}\n({value_str.strip()})'
        else:
            label_text = self._label_text

        self.config(background=color, text=label_text)

        self.after(100, self._update)
