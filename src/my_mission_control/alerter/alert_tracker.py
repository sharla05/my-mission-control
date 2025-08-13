from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Deque, Dict, Optional

from structlog.stdlib import get_logger

from my_mission_control.alerter.alert_generator import Alert
from my_mission_control.alerter.alert_rules import evaluate_alert_condition
from my_mission_control.alerter.log_line_parser import LogEntry

logger = get_logger(__name__)

VIOLATION_THRESHOLD = 3
TIME_WINDOW_MINUTES = 5
TIME_DELTA = timedelta(minutes=TIME_WINDOW_MINUTES)


class AlertTracker:
    def __init__(self):
        # For each satellite maintain queue for each of its component to store timestamp of alert condition
        self.alert_timestamps: Dict[int, Dict[str, Deque[datetime]]] = defaultdict(lambda: defaultdict(deque))
        # For each satellite maintain dictionary for each of its component to store timestamp of last alert condition
        self.last_alert_timestamp: Dict[int, Dict[str, Optional[datetime]]] = defaultdict(lambda: defaultdict(lambda: None))


    def process_log_entry(self, log_entry: LogEntry) -> Optional[Alert]:
        severity:Optional[str] = evaluate_alert_condition(log_entry)

        if not severity:
            return None

        # Add timestamp to the appropriate statellite-component pair timestamp deque
        timestamps_dq = self.alert_timestamps[log_entry.sat_id][log_entry.cmpnt]
        timestamps_dq.append(log_entry.ts)

        # Remove entries older than the violation check time delta window
        while timestamps_dq and (log_entry.ts - timestamps_dq[0]) > TIME_DELTA:
            timestamps_dq.popleft()

        # Check number of entries exceed the violation threshold
        if len(timestamps_dq) >= VIOLATION_THRESHOLD:
            first_ts = timestamps_dq[0]
            last_alert_ts = self.last_alert_timestamp[log_entry.sat_id][log_entry.cmpnt]

            if last_alert_ts is None or first_ts > last_alert_ts:
                # Generate Alert
                alert = Alert(log_entry.sat_id, severity, log_entry.cmpnt, first_ts)

                # Save timestamp that generated Alert, used as starting point to determine next alert
                self.last_alert_timestamp[log_entry.sat_id][log_entry.cmpnt] = log_entry.ts
                return alert