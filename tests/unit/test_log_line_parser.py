from datetime import datetime
from typing import Optional

import pytest

from my_mission_control.alerter.log_line_parser import parse_log_line
from my_mission_control.entity.log_entry import LogEntry


def test_parse_line_valid():
    line = "20250807 19:46:00.000|1000|17|15|9|8|7.8|BATT"
    log_entry: Optional[LogEntry] = parse_log_line(line)
    assert log_entry is not None
    assert log_entry.timestamp == datetime(2025, 8, 7, 19, 46, 0)
    assert log_entry.satellite_id == 1000
    assert log_entry.red_high_limit == 17
    assert log_entry.yellow_high_limit == 15
    assert log_entry.yellow_low_limit == 9
    assert log_entry.red_low_limit == 8
    assert log_entry.raw_value == 7.8
    assert log_entry.component == "BATT"


# --- Invalid Cases ---


def test_parse_line_missing_fields():
    line = "20250807 19:46:00.000|1000|17|15|9|8|7.8"
    log_entry: Optional[LogEntry] = parse_log_line(line)
    assert log_entry is None


def test_parse_line_extra_fields():
    line = "20250807 19:46:00.000|1000|17|15|9|8|7.8|BATT|EXTRA"
    log_entry: Optional[LogEntry] = parse_log_line(line)
    assert log_entry is None


def test_parse_line_bad_timestamp():
    line = "2025/08/07 19:46:00|1000|17|15|9|8|7.8|BATT"
    log_entry: Optional[LogEntry] = parse_log_line(line)
    assert log_entry is None


def test_parse_line_non_numeric_comp_id():
    line = "20250807 19:46:00.000|abc|17|15|9|8|7.8|BATT"
    log_entry: Optional[LogEntry] = parse_log_line(line)
    assert log_entry is None


def test_parse_line_non_numeric_red_high():
    line = "20250807 19:46:00.000|1000|high|15|9|8|7.8|BATT"
    log_entry: Optional[LogEntry] = parse_log_line(line)
    assert log_entry is None


def test_parse_line_non_numeric_red_low():
    line = "20250807 19:46:00.000|1000|17|15|9|low|7.8|BATT"
    log_entry: Optional[LogEntry] = parse_log_line(line)
    assert log_entry is None


def test_parse_line_non_numeric_raw():
    line = "20250807 19:46:00.000|1000|17|15|9|8|raw|BATT"
    log_entry: Optional[LogEntry] = parse_log_line(line)
    assert log_entry is None
