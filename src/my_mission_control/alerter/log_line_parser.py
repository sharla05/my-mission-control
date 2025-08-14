"""
Parses telemetry log file lines into structured LogEntry objects.
"""

from dataclasses import dataclass
from datetime import datetime
import os
from typing import Optional

from structlog.stdlib import get_logger

from my_mission_control.entity.log_entry import LogEntry

TIME_FORMAT_INPUT = "%Y%m%d %H:%M:%S.%f"
DELIMITER = os.getenv("DELIMITER", "|")
INPUT_FORMAT = "<timestamp>|<satellite-id>|<red-high-limit>|<yellow-high-limit>|<yellow-low-limit>|<red-low-limit>|<raw-value>|<component>"
EXPECTED_FIELD_COUNT = len(INPUT_FORMAT.split("|"))


logger = get_logger(__name__)


def parse_log_line(line) -> Optional[LogEntry]:
    """
    Parse a telemetry log line into a LogEntry object.
    Returns None if the line is malformed or parsing fails.
    """
    parts = line.strip().split(DELIMITER)
    if len(parts) != EXPECTED_FIELD_COUNT:
        logger.warning(f"Invalid line, expected {EXPECTED_FIELD_COUNT} fields, got {len(parts)}")
        return None

    try:
        ts_str, sat_id, rhl, yhl, yll, rll, val, cmpnt = parts
        ts = datetime.strptime(ts_str, TIME_FORMAT_INPUT)
        return LogEntry(ts, int(sat_id), int(rhl), int(yhl), int(yll), int(rll), float(val), cmpnt)
    except Exception as e:
        logger.error(f"Failed to parse line: '{line}' - {e}", exc_info=True)
        return None
