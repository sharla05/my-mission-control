import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Optional

from structlog.stdlib import get_logger

from my_mission_control.alerter.alert_generator import Alert
from my_mission_control.alerter.alert_tracker import AlertTracker
from my_mission_control.alerter.log_line_parser import LogEntry, parse_log_line



logger = get_logger(__name__)



def process_log_file(log_file: str) -> List[dict]:
    """
    Process log file line-by-line and generate alert when number of violation within time window exceed the threshold.
    """
    alerts: List[dict] = []
    alert_tracker = AlertTracker()
    print("")

    with open(log_file, "r") as log_lines:
        for line in log_lines:
            log_entry: LogEntry|None = parse_log_line(line)

            if log_entry is None:
                continue

            alert: Alert | None = alert_tracker.process_log_entry(log_entry)

            if alert is None:
                continue

            alerts.append(alert.to_dict())

    # logger.info(json.dumps(alerts))
    return alerts
