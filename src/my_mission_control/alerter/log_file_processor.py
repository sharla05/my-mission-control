from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Optional

from structlog.stdlib import get_logger

from my_mission_control.alerter.log_line_parser import parse_log_line
from my_mission_control.entity.alert import Alert
from my_mission_control.entity.log_entry import LogEntry

VIOLATION_THRESHOLD = 3
TIME_WINDOW_MINUTES = 5
TIME_DELTA = timedelta(minutes=TIME_WINDOW_MINUTES)

COMPONENT_TSTAT = "TSTAT"
COMPONENT_BATT = "BATT"
SEVERITY_RED_HIGH = "RED HIGH"
SEVERITY_RED_LOW = "RED LOW"

logger = get_logger(__name__)


def is_alert_condition(log_entry: LogEntry) -> bool:
    assert log_entry is not None, "log_entry must not be None"

    # Battery alert: Only consider battery voltage readings that are under the red-low-limit
    if log_entry.component == COMPONENT_BATT:
        return log_entry.raw_value < log_entry.red_low_limit

    # Thermostat alert: Only consider thermostat readings that exceed the red-high-limit
    if log_entry.component == COMPONENT_TSTAT:
        return log_entry.raw_value > log_entry.red_high_limit

    return False


def process_log_file(log_file: str) -> List[dict]:
    """
    Process log file line-by-line and generate alert when number of violation within time window exceed the threshold.
    """
    # For each satellite maintain queue for each of its component to store timestamp of alert condition
    violation_tss_by_sat_cmpnt: Dict[int, Dict[str, Deque[datetime]]] = defaultdict(lambda: defaultdict(deque))

    # For each satellite maintain dictionary for each of its component to store timestamp of last alert condition
    last_alert_ts_by_sat_cmpnt: Dict[int, Dict[str, Optional[datetime]]] = defaultdict(lambda: defaultdict(lambda: None))
    alerts: List[dict] = []

    with open(log_file, "r") as log_lines:
        for line in log_lines:
            log_entry = parse_log_line(line)

            if log_entry is None:
                continue

            if not is_alert_condition(log_entry):
                continue

            # Add timestamp to the appropriate statellite-component pair deque
            sat_cmpnt_violations_dq = violation_tss_by_sat_cmpnt[log_entry.satellite_id][log_entry.component]
            sat_cmpnt_violations_dq.append(log_entry.timestamp)

            # Remove entries older than the violation check time delta window
            while sat_cmpnt_violations_dq and (log_entry.timestamp - sat_cmpnt_violations_dq[0]) > TIME_DELTA:
                sat_cmpnt_violations_dq.popleft()

            # print(f"sat_cmpnt_violations_dq: [{sat_id}][{cmpnt}]", sat_cmpnt_violations_dq)

            # Check number of entries exceed the violation threshold
            if len(sat_cmpnt_violations_dq) >= VIOLATION_THRESHOLD:
                first_ts = sat_cmpnt_violations_dq[0]
                last_alert_ts = last_alert_ts_by_sat_cmpnt[log_entry.satellite_id][log_entry.component]

                if last_alert_ts is None or first_ts > last_alert_ts:
                    severity = SEVERITY_RED_HIGH if log_entry.component == COMPONENT_TSTAT else SEVERITY_RED_LOW
                    alert = Alert(log_entry.satellite_id, severity, log_entry.component, first_ts)
                    alerts.append(alert.to_dict())

                    # last_alert_time[log_entry.sat_id][log_entry.cmpnt] = first_ts # should be 'ts', that is, last timestamp of violation entry
                    last_alert_ts_by_sat_cmpnt[log_entry.satellite_id][log_entry.component] = log_entry.timestamp  # should be 'ts', that is, last timestamp of violation entry

    # logger.info(json.dumps(alerts))
    return alerts
