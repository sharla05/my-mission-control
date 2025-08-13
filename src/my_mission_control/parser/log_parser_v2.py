import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Optional

from structlog.stdlib import get_logger

TIME_FORMAT_INPUT = "%Y%m%d %H:%M:%S.%f"
TIME_FORMAT_OUTPUT = "%Y-%m-%dT%H:%M:%S.%fZ"
DELIMITER = "|"
INPUT_FORMAT = "<timestamp>|<satellite-id>|<red-high-limit>|<yellow-high-limit>|<yellow-low-limit>|<red-low-limit>|<raw-value>|<component>"
EXPECTED_FIELD_COUNT = len(INPUT_FORMAT.split(DELIMITER))

VIOLATION_THRESHOLD = 3
TIME_WINDOW_MINUTES = 5
TIME_DELTA = timedelta(minutes=TIME_WINDOW_MINUTES)

COMPONENT_TSTAT = "TSTAT"
COMPONENT_BATT = "BATT"
SEVERITY_RED_HIGH = "RED HIGH"
SEVERITY_RED_LOW = "RED LOW"

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


def is_alert_condition(log_entry: LogEntry) -> bool:
    assert log_entry is not None, "log_entry must not be None"

    # Battery alert: Only consider battery voltage readings that are under the red-low-limit
    if log_entry.cmpnt == COMPONENT_BATT:
        return log_entry.val < log_entry.rll

    # Temperature alert: Only consider thermostat readings that exceed the red-high-limit
    if log_entry.cmpnt == COMPONENT_TSTAT:
        return log_entry.val > log_entry.rhl

    return False


def process_log_file(log_file: str) -> List[dict]:
    """
    Process log file line-by-line and generate alert when number of violation within time window exceed the threshold.
    """
    # For each satellite maintain queue for each of its component to store timestamp of alert condition
    violation_tss_by_sat_cmpnt: Dict[int, Dict[str, Deque[datetime]]] = defaultdict(lambda: defaultdict(deque))
    last_alert_ts_by_sat_cmpnt: Dict[int, Dict[str, Optional[datetime]]] = defaultdict(lambda: defaultdict(lambda: None))
    alerts: List[dict] = []
    print("")

    with open(log_file, "r") as log_lines:
        for line in log_lines:
            log_entry = parse_log_line(line)

            if log_entry is None:
                continue

            if not is_alert_condition(log_entry):
                continue

            # Add timestamp to the appropriate statellite-component pair deque
            sat_cmpnt_violations_dq = violation_tss_by_sat_cmpnt[log_entry.sat_id][log_entry.cmpnt]
            sat_cmpnt_violations_dq.append(log_entry.ts)

            # Remove entries older than the violation check time delta window
            while sat_cmpnt_violations_dq and (log_entry.ts - sat_cmpnt_violations_dq[0]) > TIME_DELTA:
                sat_cmpnt_violations_dq.popleft()

            # print(f"sat_cmpnt_violations_dq: [{sat_id}][{cmpnt}]", sat_cmpnt_violations_dq)

            # Check number of entries exceed the violation threshold
            if len(sat_cmpnt_violations_dq) >= VIOLATION_THRESHOLD:
                first_ts = sat_cmpnt_violations_dq[0]
                last_alert_ts = last_alert_ts_by_sat_cmpnt[log_entry.sat_id][log_entry.cmpnt]

                if last_alert_ts is None or first_ts > last_alert_ts:
                    severity = SEVERITY_RED_HIGH if log_entry.cmpnt == COMPONENT_TSTAT else SEVERITY_RED_LOW
                    alert = {
                        "satelliteId": log_entry.sat_id,
                        "severity": severity,
                        "component": log_entry.cmpnt,
                        "timestamp": first_ts.strftime(TIME_FORMAT_OUTPUT),
                    }
                    alerts.append(alert)

                    # last_alert_time[log_entry.sat_id][log_entry.cmpnt] = first_ts # should be 'ts', that is, last timestamp of violation entry
                    last_alert_ts_by_sat_cmpnt[log_entry.sat_id][log_entry.cmpnt] = log_entry.ts  # should be 'ts', that is, last timestamp of violation entry

    # logger.info(json.dumps(alerts))
    return alerts
