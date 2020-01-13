from datetime import datetime
import logging
from os import remove
from pathlib import Path
from shutil import copy


class ArchiveManager:
    def __init__(self,
                 path='.', fname='data', fextension='.csv',
                 delimiter='\t', loglevel=logging.INFO):
        """
        The basic save utility bundled into the test sequencer.  The archive \
        manager is geared towards common manufacturing environments in which \
        tab-delimited text files are common.

        :param path: the path on which to save the data, not including the \
        file name
        :param fname: the file name
        :param fextension: the file extension
        :param delimiter: the delimiter or separator between fields
        :param loglevel: the logging level, for instance 'logging.INFO'
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self._fname = fname
        self._fextension = fextension
        self._path = Path(path)
        self._delimiter = delimiter

    def save(self, point: dict):
        """
        Takes a point of data supplied as a dict and, depending on existing
        conditions, will archive the data point on the disk.  Three conditions
        possible at save time:

         * Data file does not exist
         * Data file exists and is compatible with the current data point \
         (the header strings match)
         * Data file exists, but is not compatible with the current data \
         point (the header strings do not match)

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
        the data to be saved
        :return: None
        """
        destination_path = self._path / (self._fname + self._fextension)

        headers = list(point.keys())
        header_string = f'{self._delimiter.join(headers)}\n'

        data = []
        for _, value in point.items():
            if isinstance(value, str):
                data.append(value)
            elif isinstance(value, int):
                data.append(f'{value}')
            elif isinstance(value, float):
                data.append(f'{value: .03f}')
            else:
                try:
                    # convert from pint-style values
                    data.append(f'{value.magnitude: .03f}')
                except AttributeError:
                    data.append(str(value))  # this is the catch-all

        data_string = f'{self._delimiter.join(data)}\n'

        # check for the header string
        header_changed = False
        try:
            # if the header strings do not match, then set the
            # 'create_new_file' flag
            with open(destination_path, 'r') as f:
                old_header_string = f.readline()
                if old_header_string != header_string:
                    self._logger.info(
                        f'header strings do not match, '
                        f'"{old_header_string.strip()}" vs '
                        f'"{header_string.strip()}"')
                    header_changed = True
        except FileNotFoundError:
            # if the file is not found, then create a new file
            self._logger.info(f'file "{destination_path}" not found...')

        if header_changed:
            # rename the old file using a timestamp
            now = str(datetime.now().timestamp())
            now = now.split('.')[0]

            new_path = self._path / (self._fname + now + self._fextension)
            self._logger.info(f'attempting to copy "{destination_path}" '
                              f'to "{new_path}"...')
            copy(destination_path, new_path)
            remove(destination_path)

        # write the header string
        if not destination_path.exists():
            self._logger.info(f'"{destination_path}" does not exist, creating'
                              f' with new header: "{header_string.strip()}"')
            with open(destination_path, 'w') as f:
                f.write(header_string)

        # write the data string
        self._logger.info(f'appending data: "{data_string.strip()}"')
        with open(destination_path, 'a') as f:
            f.write(data_string)
