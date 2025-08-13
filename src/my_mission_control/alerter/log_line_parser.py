
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from structlog.stdlib import get_logger

TIME_FORMAT_INPUT = "%Y%m%d %H:%M:%S.%f"
DELIMITER = "|"
INPUT_FORMAT = "<timestamp>|<satellite-id>|<red-high-limit>|<yellow-high-limit>|<yellow-low-limit>|<red-low-limit>|<raw-value>|<component>"
EXPECTED_FIELD_COUNT = len(INPUT_FORMAT.split(DELIMITER))


logger = get_logger(__name__)


@dataclass
class LogEntry:
    ts: datetime
    sat_id: int
    rhl: int
    yhl: int
    yll: int
    rll: int
    val: float
    cmpnt: str


def parse_log_line(line) -> Optional[LogEntry]:
    """
    Parse single line and return timestamp, satellit_id, red_high_limit, yellow_high_limit,
    yellow_low_limit, red_low_limit, raw_value, component
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