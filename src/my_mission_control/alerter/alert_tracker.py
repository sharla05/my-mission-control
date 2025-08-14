"""
Tracks and evaluates alert conditions for satellite telemetry components.

Uses component-specific strategies to determine if a log entry triggers an alert.
Alerts are generated when violations exceed a defined threshold within a time window.
"""

import os
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Deque, Dict, Optional

from structlog.stdlib import get_logger

from my_mission_control.alerter.alert_strategy import AlertEvalStrategy
from my_mission_control.config.settings import AlertRuleCfg
from my_mission_control.entity.alert import Alert
from my_mission_control.entity.log_entry import LogEntry
from my_mission_control.utils.utility import get_env_var_int

logger = get_logger(__name__)


TIME_DELTA: timedelta = timedelta(minutes=AlertRuleCfg.ALERT_VIOLATION_TIME_WINDOW_MINUTES)


class AlertTracker:
    """
    Tracks alerts conditions for satellite components over time.

    Maintains the timestamp queues and applies evaluation strategies to determine whether alerts should be triggered.
    """

    def __init__(self, alert_eval_strategy_map: Dict[str, AlertEvalStrategy]):
        """
        Initializes the AlertTracker with evaluation stratergies.

        Args:
            alert_evaluation_stragegy_map (Dict[str, AlertEvalStrategy]):
            Mapping of component names to their alert evaluation strategies.
        """
        self.alert_eval_strategy_map = alert_eval_strategy_map
        # For each satellite maintain queue for each of its component to store timestamp of alert condition
        self.alert_timestamps: Dict[int, Dict[str, Deque[datetime]]] = defaultdict(lambda: defaultdict(deque))
        # For each satellite maintain dictionary for each of its component to store timestamp of last alert condition
        self.last_alert_timestamp: Dict[int, Dict[str, Optional[datetime]]] = defaultdict(lambda: defaultdict(lambda: None))

    def process_log_entry(self, log_entry: LogEntry) -> Optional[Alert]:
        """
        Processes a log entry and determines if an alert should be generated.

        Args:
            log_entry (LogEntry): A structured log entry containing satellite data.

        Returns:
            Optional[Alert]: An Alert object if conditions are met; otherwise, None.
        """

        def eval_alert_condition(log_entry: LogEntry):
            """
            Evaluates the alert condition for a given log entry.

            Args:
                log_entry (LogEntry): The log entry to evaluate.

            Returns:
                Optional[str]: Severity level if an alert condition is met; othersise, None.
            """
            eval_strategy = self.alert_eval_strategy_map[log_entry.component]
            if not eval_strategy:
                logger.warning(f"No alert evaluation strategy found for {log_entry.component}")
                return None
            return eval_strategy.evaluate(log_entry)

        severity: Optional[str] = eval_alert_condition(log_entry)

        if not severity:
            return None

        # Add timestamp to the appropriate statellite-component pair timestamp deque
        timestamps_dq = self.alert_timestamps[log_entry.satellite_id][log_entry.component]
        timestamps_dq.append(log_entry.timestamp)

        # Remove entries older than the violation check time delta window
        while timestamps_dq and (log_entry.timestamp - timestamps_dq[0]) > TIME_DELTA:
            timestamps_dq.popleft()

        # Check number of entries exceed the violation threshold
        if len(timestamps_dq) >= AlertRuleCfg.ALERT_VIOLATION_COUNT_THRESHOLD:
            first_ts = timestamps_dq[0]
            last_alert_ts = self.last_alert_timestamp[log_entry.satellite_id][log_entry.component]

            if last_alert_ts is None or first_ts > last_alert_ts:
                # Generate Alert
                alert = Alert(log_entry.satellite_id, severity, log_entry.component, first_ts)

                # Save timestamp that generated Alert, used as starting point to determine next alert
                self.last_alert_timestamp[log_entry.satellite_id][log_entry.component] = log_entry.timestamp
                return alert
        return None
