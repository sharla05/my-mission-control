import os
import sys
import tempfile

from structlog.stdlib import get_logger

from my_mission_control.entrypoints.cli import main

logger = get_logger(__name__)

LOG_DATA = """\
20180101 23:01:09.521|1000|17|15|9|8|7.8|BATT
20180101 23:02:11.302|1000|17|15|9|8|7.7|BATT
20180101 23:04:11.531|1000|17|15|9|8|7.9|BATT
20180101 23:05:07.421|1001|17|15|9|8|7.9|BATT
"""

EXPECTED_OUTPUT_JSON_STRING = """
[
    {
        "satelliteId": 1000,
        "severity": "RED LOW",
        "component": "BATT",
        "timestamp": "2018-01-01T23:01:09.521000Z"
    }
]
"""


def test_main_with_temp_file(capsys, monkeypatch):
    """
    Test the main function by creating a temporary log file and passing its path.
    """

    tmp_file = None
    try:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write(LOG_DATA)
            tmp.flush()
            tmp_file = tmp.name

        # Simulate a command-line argument using the temporary file's path
        monkeypatch.setattr(sys, "argv", ["dummy_cli_script_name", tmp_file])

        # Invoke the main function
        main()

        actual_output = capsys.readouterr().out
        # print("output: ", actual_output)

        # Load the expected output string into a Python object
        expected_output = EXPECTED_OUTPUT_JSON_STRING
        # print("expected_output: ", expected_output)

        # Split both strings into lists of lines
        actual_lines = actual_output.splitlines()
        expected_lines = expected_output.splitlines()

        # print("actual_lines: \n", actual_lines)
        # print("expected_lines: \n", expected_lines)

        # Compare the lists of lines directly
        assert actual_lines == expected_lines  # nosec

    finally:
        # Clean up the temprary file
        if tmp_file and os.path.exists(tmp_file):
            os.remove(tmp_file)
