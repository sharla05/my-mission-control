from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import List

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


def parse_log_line(line):
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
        return (
            ts,
            int(sat_id),
            int(rhl),
            int(yhl),
            int(yll),
            int(rll),
            float(val),
            cmpnt,
        )
    except Exception as e:
        logger.error(f"Failed to parse line: '{line}' - {e}", exc_info=True)
        return None


def process_log_file(log_file: str) -> List[dict]:
    """
    Process log file line-by-line and generate alert when number of violation within time window exceed the threshold.
    """
    violation_by_sat_cmpnt = defaultdict(lambda: defaultdict(deque))
    last_alert_time = defaultdict(lambda: defaultdict(lambda: None))
    alerts = []

    with open(log_file, "r") as log_lines:
        for line in log_lines:
            parsed_line = parse_log_line(line)
            if not parsed_line:
                continue  # Ignore malformed log entries

            ts, sat_id, rhl, yhl, yll, rll, val, cmpnt = parsed_line

            if cmpnt not in (COMPONENT_TSTAT, COMPONENT_BATT):
                continue  # Ignore log entries not related to battery or thermostat

            # Battery alert: Only consider battery voltage readings that are under the red-low-limit
            if cmpnt == COMPONENT_BATT and val >= rll:
                continue

            # Thermostat alert: Only consider thermostat readings that exceed the red-high-limit
            if cmpnt == COMPONENT_TSTAT and val <= rhl:
                continue

            # print("violation lines: ", ts, sat_id, rhl, yhl, yll, rll, val, cmpnt)

            # Add timestamp to the appropriate statellite-component pair deque
            sat_cmpnt_violations_dq = violation_by_sat_cmpnt[sat_id][cmpnt]
            sat_cmpnt_violations_dq.append(ts)

            # Remove entries older than the violation check time delta window
            while sat_cmpnt_violations_dq and (ts - sat_cmpnt_violations_dq[0]) > TIME_DELTA:
                sat_cmpnt_violations_dq.popleft()

            # print(f"sat_cmpnt_violations_dq: [{sat_id}][{cmpnt}]", sat_cmpnt_violations_dq)

            # Check number of entries exceed the violation threshold
            if len(sat_cmpnt_violations_dq) >= VIOLATION_THRESHOLD:
                first_ts = sat_cmpnt_violations_dq[0]
                last_alert_ts = last_alert_time[sat_id][cmpnt]

                if last_alert_ts is None or first_ts > last_alert_ts:
                    severity = SEVERITY_RED_HIGH if cmpnt == COMPONENT_TSTAT else SEVERITY_RED_LOW
                    alert = {
                        "satelliteId": sat_id,
                        "severity": severity,
                        "component": cmpnt,
                        "timestamp": first_ts.strftime(TIME_FORMAT_OUTPUT),
                    }
                    alerts.append(alert)

                    last_alert_time[sat_id][cmpnt] = first_ts  # should be 'ts', that is, last timestamp of violation entry

    # logger.info(json.dumps(alerts))
    return alerts
