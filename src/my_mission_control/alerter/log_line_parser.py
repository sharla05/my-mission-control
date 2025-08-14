"""
Parses telemetry log file lines into structured LogEntry objects.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from structlog.stdlib import get_logger

from my_mission_control.config.settings import InputLogFileCfg
from my_mission_control.entity.log_entry import LogEntry

logger = get_logger(__name__)


def parse_log_line(line) -> Optional[LogEntry]:
    """
    Parse a telemetry log line into a LogEntry object.
    Returns None if the line is malformed or parsing fails.
    """
    parts = line.strip().split(InputLogFileCfg.LOG_LINE_DELIMITER)
    if len(parts) != InputLogFileCfg.LOG_LINE_EXPECTED_FIELD_COUNT:
        logger.warning(f"Invalid line, expected {InputLogFileCfg.LOG_LINE_EXPECTED_FIELD_COUNT} fields, got {len(parts)}")
        return None

    try:
        ts_str, sat_id, rhl, yhl, yll, rll, val, cmpnt = parts
        ts = datetime.strptime(ts_str, InputLogFileCfg.LOG_LINE_TIMESTAMP_FORMAT)
        return LogEntry(ts, int(sat_id), int(rhl), int(yhl), int(yll), int(rll), float(val), cmpnt)
    except Exception as e:
        logger.error(f"Failed to parse line: '{line}' - {e}", exc_info=True)
        return None
