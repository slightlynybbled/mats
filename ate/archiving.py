from datetime import datetime
import logging
from os import remove
from pathlib import Path
from shutil import copy


class ArchiveManager:
    def __init__(self, path, fname='data', fextension='.csv', delimiter='\t', loglevel=logging.DEBUG):
        """
        The basic save utility bundled into the test sequencer.

        :param path:
        :param fname:
        :param fextension:
        :param delimiter:
        :param loglevel:
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self._fname = fname
        self._fextension = fextension
        self._path = Path(path)
        self._delimiter = delimiter

    def save(self, point: dict):
        destination_path = self._path / (self._fname + self._fextension)

        headers = list(point.keys())
        header_string = f'{self._delimiter.join(headers)}\n'

        data = []
        for _, value in point.items():
            if isinstance(value, str):
                data.append(value)
            else:
                try:
                    # convert from pint-style values
                    data.append(f'{value.magnitude: .03f}')
                except AttributeError:
                    data.append(f'{value: .03f}')

        data_string = f'{self._delimiter.join(data)}\n'

        # check for the header string
        header_changed = False
        try:
            # if the header strings do not match, then set the 'create_new_file' flag
            with open(destination_path, 'r') as f:
                old_header_string = f.readline()
                if old_header_string != header_string:
                    self._logger.info(f'header strings do not match, "{old_header_string.strip()}" vs "{header_string.strip()}"')
                    header_changed = True
        except FileNotFoundError:
            # if the file is not found, then create a new file
            self._logger.info(f'file "{destination_path}" not found...')

        if header_changed:
            # rename the old file using a timestamp
            now = str(datetime.now().timestamp())
            now = now.split('.')[0]

            new_path = self._path / (self._fname + now + self._fextension)
            self._logger.info(f'attempting to copy "{destination_path}" to "{new_path}"...')
            copy(destination_path, new_path)
            remove(destination_path)

        # write the header string
        if not destination_path.exists():
            self._logger.info(f'"{destination_path}" does not exist, creating'
                              f' with new header: "{header_string.strip()}"')
            with open(destination_path, 'w') as f:
                f.write(header_string)

        # write the data string
        self._logger.debug(f'appending data: "{data_string.strip()}"')
        with open(destination_path, 'a') as f:
            f.write(data_string)


if __name__ == '__main__':
    from time import sleep
    import pint
    logging.basicConfig(level=logging.DEBUG)
    am = ArchiveManager(path='.')

    unit = pint.UnitRegistry()

    sleep(2.0)
    am.save(point={'a': 1.0, 'b': 2.0, 'c': 3.0 * unit.rpm})
    am.save(point={'a': 1.0, 'b': 2.0, 'c': 3.0 * unit.rpm})
    am.save(point={'a': 1.0, 'b': 2.0, 'c': 3.0 * unit.rpm})
    am.save(point={'a': 1.0, 'b': 2.0, 'c': 3.0 * unit.rpm})
    am.save(point={'a': 1.0, 'b': 2.0, 'c': 3.0 * unit.rpm})

    sleep(2.0)
    am.save(point={'aa': 1.0, 'b': 2.0, 'c': 3.0})
    #am.save(point={'a': 1.0, 'b': 2.0, 'c': 3.0})
    #am.save(point={'aa': 1.0, 'b': 2.0, 'c': 3.0})
    #am.save(point={'a': 1.0, 'b': 2.0, 'c': 3.0})
    #am.save(point={'aa': 1.0, 'b': 2.0, 'c': 3.0})
