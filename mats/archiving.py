from datetime import datetime
import logging
from os import remove
from os.path import splitext
from pathlib import Path
from shutil import copy


class ArchiveManager:
    def __init__(self,
                 path='.', fname='data.txt',
                 delimiter='\t', loglevel=logging.INFO):
        """
        The basic save utility bundled into the test sequencer.  The archive \
        manager is geared towards common manufacturing environments in which \
        tab-delimited text files are common.

        :param path: the path on which to save the data, not including the \
        file name
        :param fname: the file name
        :param delimiter: the delimiter or separator between fields
        :param loglevel: the logging level, for instance 'logging.INFO'
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self._fname = fname
        self._path = Path(path)
        self._delimiter = delimiter

    def save(self, point: dict):
        """
        Takes a point of data supplied as a dict and, depending on existing
        conditions, will archive the data point on the disk.  Each ``point``
        represents a single row of data representing the execution of a
        single instance of the test execution.  Each key of the ``dict`` has
        will represent the parameter being measured.

        Three conditions possible at save time:

         * Data file does not exist
         * Data file exists and is compatible with the current data point \
         (the headings and header strings match)
         * Data file exists, but is not compatible with the current data \
         point (the heading and header strings do not match)

        When the data file does not exist, then the ``save()`` method will
        create the new data file at ``<fname>.<extension>``.

        When the data file exists at ``<fname>.<extension>`` and is compatible
        with the current data point, then the ``save()`` method will simply
        append the new data point to previous data in a tabular format.

        Finally, when the current data point is deemed incompatible with the
        previous data, then the ``save()`` method will copy the old file to
        ``<fname>_<datetime>.<extension>`` and then create a new file at
        ``<fname>.<extension>`` under which data will be collected until a new
        format is once again detected.

        :param point: a ``dict`` containing key: value pairs which specify \
        the data to be saved in {'heading': {'value': value}}; the inner \
        dictionary may also contain a ``dict`` called ``criteria`` which \
        will contain the ``pass_if``, ``min``, or ``max`` values allowed
        :return: None
        """
        destination_path = self._path / self._fname

        headers = list(point.keys())

        heading_string = ''
        for header in headers:
            heading_fragments = []
            criteria = point[header].get('criteria')
            if criteria is not None:
                if 'pass_if' in criteria.keys():
                    heading_fragments.append(f"pass_if={criteria['pass_if']}")
                if 'min' in criteria.keys():
                    heading_fragments.append(f"min={criteria['min']:.3g}")
                if 'max' in criteria.keys():
                    heading_fragments.append(f"max={criteria['max']:.3g}")

                heading_string += (header + ':'
                                   + ','.join(heading_fragments) + '\n')

        header_string = heading_string + f'\n{self._delimiter.join(headers)}\n'

        data = []
        for _, value in point.items():
            v = value.get('value')
            if isinstance(v, str):
                data.append(v)
            elif isinstance(v, int):
                data.append(f'{v}')
            elif isinstance(v, float):
                data.append(f'{v: .03f}')
            else:
                try:
                    # convert from pint-style values
                    data.append(f'{v.magnitude: .03f}')
                except AttributeError:
                    data.append(str(v))  # this is the catch-all

        data_string = f'{self._delimiter.join(data)}\n'

        # check for the header string
        header_changed = False
        try:
            # if the header strings do not match, then set the
            # 'create_new_file' flag
            with open(destination_path, 'r') as f:
                len_new_header_string = len(header_string)
                old_header_string = f.read(len_new_header_string)

                if old_header_string != header_string:
                    self._logger.info(
                        'header strings do not match')
                    header_changed = True
        except FileNotFoundError:
            # if the file is not found, then create a new file
            self._logger.info(f'file "{destination_path}" not found...')

        if header_changed:
            # rename the old file using a timestamp
            now = str(datetime.now().timestamp())
            now = now.split('.')[0]

            parts = list(splitext(self._fname))
            parts.insert(1, now)
            new_path = self._path / ''.join(parts)

            self._logger.info(f'attempting to copy "{destination_path}" '
                              f'to "{new_path}"...')
            copy(destination_path, new_path)
            remove(destination_path)

        # write the header string
        if not destination_path.exists():
            self._logger.info(f'"{destination_path}" does not exist, creating'
                              f' with new heading')
            with open(destination_path, 'w') as f:
                f.write(header_string)

        # write the data string
        self._logger.info(f'appending data: "{data_string.strip()}"')
        with open(destination_path, 'a') as f:
            f.write(data_string)
