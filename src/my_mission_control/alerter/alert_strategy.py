from abc import ABC
from typing import Optional

from my_mission_control.alerter.log_line_parser import LogEntry

SEVERITY_RED_HIGH = "RED HIGH"
SEVERITY_RED_LOW = "RED LOW"


class AlertEvalStrategy(ABC):
    def evaluate(self, log_entry: LogEntry) -> Optional[str]:
        pass

class RedLowAlertStrategy(AlertEvalStrategy):
    def evaluate(self, log_entry: LogEntry) -> Optional[str]:
        """
        Only consider readings that are under the red-low-limit
        """
        if log_entry.val < log_entry.rll:
                return SEVERITY_RED_LOW
        return None


class RedHighAlertStrategy(AlertEvalStrategy):
    def evaluate(self, log_entry: LogEntry) -> Optional[str]:
        """
        Only readings that exceed the red-high-limit
        """
        if log_entry.val > log_entry.rhl:
                return SEVERITY_RED_HIGH
        return None
