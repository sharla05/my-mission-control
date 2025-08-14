"""
Processes satellite telemetry log files to generate alerts based on component-specific violation thresholds.

Each log line is parsed into a structured LogEntry. Alerts are triggered when violations exceed
defined thresholds within a time window, using component-specific alert evaluation strategies.
"""

from typing import Dict, List, Optional, TextIO

from structlog.stdlib import get_logger

from my_mission_control.alerter.alert_strategy import AlertEvalStrategy, RedHighAlertStrategy, RedLowAlertStrategy
from my_mission_control.alerter.alert_tracker import AlertTracker
from my_mission_control.alerter.log_line_parser import parse_log_line
from my_mission_control.config.settings import LogCfg
from my_mission_control.entity.alert import Alert
from my_mission_control.entity.log_entry import LogEntry

logger = get_logger(__name__)


def _process_log_line(line: str, alert_tracker: AlertTracker) -> Optional[Alert]:
    """
    Processes a single satellite telemetry log file line and returns an alert if one is detected.

    Each line is parsed into a LogEntry. If the number of violations for a component
    exceeds the threshold within a time window, an alert is generated using the appropriate strategy.

    Args:
        line (str): A single line from the telemetry log file.
        alert_tracker (AlertTracker): Tracker that evaluates log entries against alert thresholds.

    Returns:
        Optional[Alert]: An Alert object if a violation is detected; otherwise, None.
    """
    log_entry: Optional[LogEntry] = parse_log_line(line)

    if log_entry is None:
        logger.warning("Skipping malformed or unparseable line", line)
        return None
    alert: Optional[Alert] = alert_tracker.process_log_entry(log_entry)

    if alert is None:
        return None
    return alert


def _process_log_lines(log_lines: TextIO) -> List[dict]:
    """
    Line-by-line processes satellite telemetry log and generates alerts.

    Initializes an alert tracker with component -specific strategies and evaluates each line.
        Alerts are collected and returned as dictionaries with key in camelCase as required for reporting.

    Args:
        log_lines (TextIO): A file-like object containing telemetry log lines.

    Returns:
        List[dict]: A list of dictionaries generated from the log lines.
    """
    alerts: List[dict] = []

    # Map each component to its corresponding alert evaluation strategy
    alert_eval_strategy_map: Dict[str, AlertEvalStrategy] = {LogCfg.LOG_LINE_COMPONENT_BATT: RedLowAlertStrategy(), LogCfg.LOG_LINE_COMPONENT_TSTAT: RedHighAlertStrategy()}
    # Initialize the alert tracker with alert evaluation stragegy mapping
    alert_tracker = AlertTracker(alert_eval_strategy_map)

    for line in log_lines:
        alert = _process_log_line(line, alert_tracker)
        if alert:
            alerts.append(alert.to_dict())

    return alerts


def process_log_file(log_file: str) -> List[dict]:
    """
    Processes a satellite telemetry log file line-by-line and generates alerts.

    Opens the file, reads each line, and evaluates it using component-specific alert strategies.
    Alerts are returned as dictionaries for further reporting with required keys.

    Args:
        log_file (str): Path to the telemetry log file.

    Returns:
        List[dict]: A list of alert dictionaries generated from the log file.
    """
    with open(log_file, "r") as log_lines:
        return _process_log_lines(log_lines)
