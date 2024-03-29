from datetime import datetime
import logging
from os import remove
from pathlib import Path
from shutil import copy
from typing import Optional

from mats.test import Test


class ArchiveManager:
    """
    The default data manager that saves data in a text format which is very flexible, \
    yet maintains simplicity and compatibility with analysis tools such as pandas.

    :param path: a string or `Path` containing the path to the data file
    :param fname: data file name
    :param delimiter: the data delimiter
    :param data_format: an integer that determines which data format
    :param preamble: a string that may be appended to the beginning of a data file
    :param loglevel: the logging level
    """

    def __init__(
        self,
        path: str | Path = ".",
        fname: str = "data.txt",
        delimiter: str = "\t",
        data_format: int = 0,
        preamble: Optional[str] = None,
        loglevel=logging.INFO,
    ):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self._fname = fname
        self._path = Path(path)
        self._delimiter = delimiter
        self._format = data_format
        self._preamble = preamble

    def aggregate(
        self,
        datetime: datetime,
        is_passing: bool,
        failed: list[str],
        tests: list[Test],
    ):
        """
        Collects data set from provided information and from the tests \
        and organizes the data into a dict in preparation for saving \
        a row of data.

        :param datetime: the datetime that the test started
        :param is_passing: True/False/None indicating if the test passed, \
        failed, or was aborted
        :param failed: a list of test monikers that failed
        :param tests: a list of tests representing the test sequence
        :return:
        """
        test_data = {
            "datetime": {"value": datetime},
            "pass": {"value": is_passing},
            "failed": {"value": failed.copy()},
        }

        for t in tests:
            test_data[t.moniker] = {"value": t.value}
            if t.criteria is not None:
                test_data[t.moniker]["criteria"] = t.criteria
            for k, v in t.saved_data.items():
                test_data[k]["value"] = v

        self.save(test_data)

    def save(self, point: dict):
        """
        Data save function

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
        append the new data point to previous data in a tabular data_format.

        Finally, when the current data point is deemed incompatible with the
        previous data, then the ``save()`` method will copy the old file to
        ``<fname>_<date>.<extension>`` and then create a new file at
        ``<fname>.<extension>`` under which data will be collected until a new
        data_format is once again detected.

        :param point: a ``dict`` containing key: value pairs which specify \
        the data to be saved in {'heading': {'value': value}}; the inner \
        dictionary may also contain a ``dict`` called ``criteria`` which \
        will contain the ``pass_if``, ``min``, or ``max`` values allowed
        :return: None
        """
        if self._format == 0:
            self._save_fmt0(point)
        elif self._format == 1:
            self._save_fmt1(point)
        else:
            raise ValueError(f'data_format "{self._format}" invalid')

    def _save_fmt0(self, point: dict):
        """
        Saves data with pass/fail criteria embedded into each header according
        to "data_format 0"

        :param point: a dict containing the name, value, and pass/fail \
        criteria.
        """
        headers = list(point.keys())

        heading_string = ""
        for header in headers:
            heading_fragments = []
            criteria = point[header].get("criteria")
            if criteria is not None:
                if "pass_if" in criteria.keys():
                    heading_fragments.append(f"pass_if={criteria['pass_if']}")
                if "min" in criteria.keys():
                    heading_fragments.append(f"min={criteria['min']}")
                if "max" in criteria.keys():
                    heading_fragments.append(f"max={criteria['max']}")

                heading_string += header + ":" + ",".join(heading_fragments) + "\n"

        preamble = '' if not self._preamble else f'{self._preamble}\n'
        header_string = preamble \
                        + heading_string \
                        + f"\n{self._delimiter.join(headers)}\n"

        data = []
        for _, value in point.items():
            v = value.get("value")
            if isinstance(v, str):
                data.append(v)
            elif isinstance(v, int):
                data.append(f"{v}")
            elif isinstance(v, float):
                data.append(f"{v}")
            else:
                try:
                    # convert from pint-style values
                    data.append(f"{v.magnitude}")
                except AttributeError:
                    data.append(str(v))  # this is the catch-all

        data_string = f"{self._delimiter.join(data)}\n"

        self._save_file(header_string, data_string)

    def _save_fmt1(self, point: dict):
        """
        Saves data with pass/fail criteria embedded into each header according
        to "data_format 1"

        :param point: a dict containing the name, value, and pass/fail \
        criteria.
        """
        headers = list(point.keys())

        header_string = ""
        for header in headers:
            header_string += f"{header}\t"
            criteria = point[header].get("criteria")

            if criteria is not None:
                if "pass_if" in criteria.keys():
                    header_string += f"{header} =\t"
                if "min" in criteria.keys():
                    header_string += f"{header} >=\t"
                if "max" in criteria.keys():
                    header_string += f"{header} <=\t"

        preamble = '' if not self._preamble else f'{self._preamble}\n\n'
        header_string = preamble \
                        + header_string.strip() \
                        + "\n"

        data = []
        for header, value in point.items():
            v = value.get("value")
            if header == "failed":
                # when header is "failed", then save each failed value into
                # its own special semicolon-separated data_format
                data.append(";".join(v))
            else:
                if isinstance(v, str):
                    data.append(v)
                elif isinstance(v, int):
                    data.append(f"{v}")
                elif isinstance(v, float):
                    data.append(f"{v}")
                else:
                    try:
                        # convert from pint-style values
                        data.append(f"{v.magnitude}")
                    except AttributeError:
                        data.append(str(v))  # this is the catch-all

                criteria = point[header].get("criteria")
                if criteria is not None:
                    if "pass_if" in criteria.keys():
                        data.append(f'{criteria["pass_if"]}')
                    if "min" in criteria.keys():
                        data.append(f'{criteria["min"]}')
                    if "max" in criteria.keys():
                        data.append(f'{criteria["max"]}')

        data_string = f"{self._delimiter.join(data)}\n"

        self._save_file(header_string, data_string)

    def _save_file(self, header_string: str, data_string: str):
        """
        Saves a new file if header has changed or appends to the old file.

        :param header_string: the string containing the header
        :param data_string: the string containing the data
        """
        destination_path = self._path / self._fname

        # check for the header string
        header_changed = False
        try:
            # if the header strings do not match, then set the
            # 'create_new_file' flag
            with open(destination_path, "r") as f:
                len_new_header_string = len(header_string)
                old_header_string = f.read(len_new_header_string)

                if old_header_string != header_string:
                    self._logger.info("header strings do not match")
                    header_changed = True
        except FileNotFoundError:
            # if the file is not found, then create a new file
            self._logger.info(f'file "{destination_path}" not found...')

        if header_changed:
            now = datetime.now().strftime("%Y-%m-%dT%H%M%S")

            # rename the old file using ISO8601 timestamp
            parts = self._fname.split(".")
            parts[0] = f"{parts[0]}_{now}"
            new_path = self._path / ".".join(parts)

            self._logger.info(
                f'attempting to copy "{destination_path}" ' f'to "{new_path}"...'
            )
            copy(destination_path, new_path)
            remove(destination_path)

        # write the header string
        if not destination_path.exists():
            self._logger.info(
                f'"{destination_path}" does not exist, creating' f" with new heading"
            )
            with open(destination_path, "w") as f:
                f.write(header_string)

        # write the data string
        self._logger.info(f'appending data: "{data_string.strip()}"')
        with open(destination_path, "a") as f:
            f.write(data_string)
