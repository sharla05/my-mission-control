from typing import Dict, List

from structlog.stdlib import get_logger

from my_mission_control.alerter.alert_generator import Alert
from my_mission_control.alerter.alert_strategy import AlertEvalStrategy, RedHighAlertStrategy, RedLowAlertStrategy
from my_mission_control.alerter.alert_tracker import AlertTracker
from my_mission_control.alerter.log_line_parser import LogEntry, parse_log_line

logger = get_logger(__name__)

COMPONENT_TSTAT = "TSTAT"
COMPONENT_BATT = "BATT"

def process_log_file(log_file: str) -> List[dict]:
    """
    Process log file line-by-line and generate alert when number of violation within time window exceed the threshold.
    """
    alerts: List[dict] = []
    alert_eval_strategy_map: Dict[str, AlertEvalStrategy] = {COMPONENT_BATT:RedLowAlertStrategy(), COMPONENT_TSTAT:RedHighAlertStrategy()}
    alert_tracker = AlertTracker(alert_eval_strategy_map)
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
