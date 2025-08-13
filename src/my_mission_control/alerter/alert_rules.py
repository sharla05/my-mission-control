from typing import Optional

from structlog.stdlib import get_logger

from my_mission_control.alerter.log_line_parser import LogEntry

logger = get_logger(__name__)


COMPONENT_TSTAT = "TSTAT"
COMPONENT_BATT = "BATT"
SEVERITY_RED_HIGH = "RED HIGH"
SEVERITY_RED_LOW = "RED LOW"


def evaluate_alert_condition(log_entry: LogEntry) -> Optional[str]:
    """
    Return the severity if alert condition is matched else return None
    """
    assert log_entry is not None, "log_entry must not be None"

    # Battery alert: Only consider battery voltage readings that are under the red-low-limit
    if log_entry.cmpnt == COMPONENT_BATT and log_entry.val < log_entry.rll:
            return SEVERITY_RED_LOW

    # Temperature alert: Only consider thermostat readings that exceed the red-high-limit
    if log_entry.cmpnt == COMPONENT_TSTAT and log_entry.val > log_entry.rhl:
            return SEVERITY_RED_HIGH

    return None
