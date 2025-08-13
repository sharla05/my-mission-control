"""
Processes satellite telemetry log files to generate alerts based on component-specific violation thresholds.

Each log line is parsed into a structured LogEntry. Alerts are tiggered when violations exceed
defined thresholds within a time window, using component-specific alert evaluation strategies.
"""

from typing import Dict, List, Optional

from structlog.stdlib import get_logger

from my_mission_control.alerter.alert_strategy import AlertEvalStrategy, RedHighAlertStrategy, RedLowAlertStrategy
from my_mission_control.alerter.alert_tracker import AlertTracker
from my_mission_control.alerter.log_line_parser import parse_log_line
from my_mission_control.entity.alert import Alert
from my_mission_control.entity.log_entry import LogEntry

logger = get_logger(__name__)

# Compoent identifiers as specified in the log file, used to determine alert strategy
COMPONENT_TSTAT = "TSTAT"
COMPONENT_BATT = "BATT"


def process_log_file(log_file: str) -> List[dict]:
    """
    Processes a satellite telemetry log file line-by-line and generates alerts.

        Each line is parsed into a LogEntry. If the number of violations for a component
        exceeds the threshold within a time window, an alert is generated using the appropriate strategy.

        Args:
            log_file (str): Path to the telemetry log file.

        Returns:
            List[dict]: A list of dictionaries generated from the log file.
    """
    alerts: List[dict] = []

    # Map each component to its corresponding alert evaluation strategy
    alert_eval_strategy_map: Dict[str, AlertEvalStrategy] = {COMPONENT_BATT: RedLowAlertStrategy(), COMPONENT_TSTAT: RedHighAlertStrategy()}
    # Initialize the alert tracker with alert evaluation stragegy mapping
    alert_tracker = AlertTracker(alert_eval_strategy_map)

    with open(log_file, "r") as log_lines:
        for line in log_lines:
            log_entry: Optional[LogEntry] = parse_log_line(line)

            if log_entry is None:
                # Skip malformed or unparseable lines
                continue

            alert: Optional[Alert] = alert_tracker.process_log_entry(log_entry)

            if alert is None:
                continue

            alerts.append(alert.to_dict())

    return alerts
